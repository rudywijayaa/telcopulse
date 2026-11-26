"""Konfigurasi scraper: dimuat dari YAML dan divalidasi dengan Pydantic."""

from datetime import date
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class AppConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    app_id: str = Field(min_length=3)
    operator: str
    group: Literal["A", "B", "C"]


class ScraperConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    language: str = "id"
    country: str = "id"
    start_date: date
    batch_size: int = Field(gt=0)
    sleep_seconds: float = Field(ge=0)
    sleep_jitter: float = Field(ge=0)
    max_retries: int = Field(ge=0)
    backoff_base_seconds: float = Field(gt=0)
    checkpoint_every: int = Field(gt=0)
    output_dir: Path
    apps: dict[str, AppConfig]

    @model_validator(mode="after")
    def _check_unique_app_ids(self) -> "ScraperConfig":
        ids = [app.app_id for app in self.apps.values()]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise ValueError(f"app_id duplikat: {duplicates}")
        return self

    def apps_in_groups(self, *groups: str) -> dict[str, AppConfig]:
        return {name: app for name, app in self.apps.items() if app.group in groups}


def load_config(path: Path | str) -> ScraperConfig:
    """Melempar ValidationError jika isi file tidak valid."""
    with open(path, encoding="utf-8") as file:
        raw = yaml.safe_load(file)
    return ScraperConfig.model_validate(raw)
