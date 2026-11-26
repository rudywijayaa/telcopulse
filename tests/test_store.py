from datetime import UTC, datetime

import pyarrow.parquet as pq

from src.models import Review
from src.store import ReviewStore, ScrapeState, StateFile

MOMENT = datetime(2025, 4, 1, 0, 30, tzinfo=UTC)


def make_review(review_id="r1", **overrides):
    values = {
        "review_id": review_id,
        "app_source": "mytelkomsel",
        "app_id": "com.telkomsel.telkomselcm",
        "content": "kuota mahal",
        "rating": 1,
        "thumbs_up": 3,
        "app_version": "9.4.1",
        "reviewed_at": MOMENT,
        "reply_content": None,
        "replied_at": None,
        "sort_mode": "newest",
        "scraped_at": MOMENT,
    }
    values.update(overrides)
    return Review(**values)


def test_write_chunk_round_trips_values_and_types(tmp_path):
    store = ReviewStore(tmp_path, "mytelkomsel")
    path = store.write_chunk([make_review("r1"), make_review("r2", rating=5)])
    table = pq.read_table(path)
    assert table.num_rows == 2
    assert table.schema.field("reviewed_at").type.tz == "UTC"
    assert table.column("review_id").to_pylist() == ["r1", "r2"]
    assert table.column("reviewed_at").to_pylist()[0] == MOMENT


def test_nullable_fields_stay_null(tmp_path):
    store = ReviewStore(tmp_path, "mytelkomsel")
    path = store.write_chunk([make_review(app_version=None)])
    row = pq.read_table(path).to_pylist()[0]
    assert row["app_version"] is None
    assert row["reply_content"] is None
    assert row["replied_at"] is None


def test_chunks_are_numbered_sequentially(tmp_path):
    store = ReviewStore(tmp_path, "mytelkomsel")
    first = store.write_chunk([make_review("a")])
    second = store.write_chunk([make_review("b")])
    assert first.name == "part-00001.parquet"
    assert second.name == "part-00002.parquet"


def test_empty_chunk_writes_nothing(tmp_path):
    store = ReviewStore(tmp_path, "mytelkomsel")
    assert store.write_chunk([]) is None
    assert store.parts() == []


def test_row_count_sums_all_parts(tmp_path):
    store = ReviewStore(tmp_path, "mytelkomsel")
    store.write_chunk([make_review("a"), make_review("b")])
    store.write_chunk([make_review("c")])
    assert store.row_count() == 3


def test_no_temp_files_left_behind(tmp_path):
    store = ReviewStore(tmp_path, "mytelkomsel")
    store.write_chunk([make_review()])
    assert list(store.directory.glob("*.tmp")) == []


def test_apps_do_not_share_directories(tmp_path):
    ReviewStore(tmp_path, "mytelkomsel").write_chunk([make_review("a")])
    other = ReviewStore(tmp_path, "byu")
    assert other.parts() == []


def test_missing_state_file_gives_fresh_state(tmp_path):
    state = StateFile(tmp_path / "state.json").load()
    assert state == ScrapeState()


def test_state_round_trips_including_datetime(tmp_path):
    state_file = StateFile(tmp_path / "state.json")
    saved = ScrapeState(
        next_token="tok123",
        scraped_count=4200,
        oldest_seen=MOMENT,
        finished=True,
        finish_reason="start_date",
    )
    state_file.save(saved)
    assert state_file.load() == saved


def test_saving_again_overwrites_previous_state(tmp_path):
    state_file = StateFile(tmp_path / "state.json")
    state_file.save(ScrapeState(scraped_count=1))
    state_file.save(ScrapeState(scraped_count=2))
    assert state_file.load().scraped_count == 2
    assert list(tmp_path.glob("*.tmp")) == []
