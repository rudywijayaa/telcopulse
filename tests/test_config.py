from copy import deepcopy
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from src.config import ScraperConfig, load_config

REAL_CONFIG = Path(__file__).resolve().parents[1] / "configs" / "scraper.yaml"

VALID = {
    "start_date": "2022-07-01",
    "batch_size": 200,
    "sleep_seconds": 1.0,
    "sleep_jitter": 0.5,
    "max_retries": 5,
    "backoff_base_seconds": 5.0,
    "checkpoint_every": 5000,
    "output_dir": "data/raw",
    "apps": {
        "a": {"app_id": "com.example.a", "operator": "x", "group": "A"},
        "b": {"app_id": "com.example.b", "operator": "x", "group": "B"},
    },
}


def make(**overrides: object) -> dict:
    raw = deepcopy(VALID)
    raw.update(overrides)
    return raw


def test_real_config_loads():
    config = load_config(REAL_CONFIG)
    assert config.start_date.isoformat() == "2022-07-01"
    assert len(config.apps) == 7
    assert set(config.apps_in_groups("A")) == {"mytelkomsel", "byu", "myim3", "bimaplus"}


def test_valid_config_converts_types():
    config = ScraperConfig.model_validate(make())
    assert config.output_dir == Path("data/raw")
    assert config.language == "id"


@pytest.mark.parametrize(
    "overrides",
    [
        {"batch_size": 0},
        {"sleep_seconds": -1},
        {"backoff_base_seconds": 0},
        {"checkpoint_every": 0},
        {"start_date": "bukan-tanggal"},
        {"sleep_second": 1.0},
    ],
    ids=[
        "batch_nol",
        "jeda_negatif",
        "backoff_nol",
        "checkpoint_nol",
        "tanggal_salah",
        "kunci_asing",
    ],
)
def test_rejects_invalid_values(overrides):
    with pytest.raises(ValidationError):
        ScraperConfig.model_validate(make(**overrides))


def test_rejects_unknown_group():
    raw = make()
    raw["apps"]["a"]["group"] = "D"
    with pytest.raises(ValidationError):
        ScraperConfig.model_validate(raw)


def test_rejects_duplicate_app_id():
    raw = make()
    raw["apps"]["b"]["app_id"] = raw["apps"]["a"]["app_id"]
    with pytest.raises(ValidationError, match="duplikat"):
        ScraperConfig.model_validate(raw)


def test_rejects_missing_required_field():
    raw = make()
    del raw["start_date"]
    with pytest.raises(ValidationError):
        ScraperConfig.model_validate(raw)


def test_config_is_immutable():
    config = ScraperConfig.model_validate(make())
    with pytest.raises(ValidationError):
        config.batch_size = 1


def test_apps_in_groups_filters():
    config = ScraperConfig.model_validate(make())
    assert set(config.apps_in_groups("A")) == {"a"}
    assert set(config.apps_in_groups("A", "B")) == {"a", "b"}


def test_load_config_rejects_bad_file(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.safe_dump(make(batch_size=-5)), encoding="utf-8")
    with pytest.raises(ValidationError):
        load_config(path)
