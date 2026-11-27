from dataclasses import dataclass, fields
from datetime import UTC, datetime, timedelta

import pyarrow.parquet as pq
import pytest
from google_play_scraper import Sort

from src.config import ScraperConfig
from src.scraper import ContinuationToken, PlayStoreScraper
from src.store import ReviewStore, StateFile

NOW = datetime(2026, 11, 27, 8, 0, tzinfo=UTC)
RECENT = datetime(2025, 12, 1, tzinfo=UTC)
IN_WINDOW = datetime(2022, 8, 1, tzinfo=UTC)
TOO_OLD = datetime(2022, 5, 1, tzinfo=UTC)


@dataclass
class Token:
    token: str | None


class FakePlayStore:
    def __init__(self, pages, fail_times=0):
        self.pages = pages
        self.fail_times = fail_times
        self.calls = []
        self.tokens = []

    def __call__(self, app_id, *, lang, country, sort, count, continuation_token=None):
        self.calls.append(continuation_token.token if continuation_token else None)
        self.tokens.append(continuation_token)
        if self.fail_times > 0:
            self.fail_times -= 1
            return [], Token(None)
        index = int(continuation_token.token[1:]) if continuation_token else 0
        next_token = Token(f"t{index + 1}") if index + 1 < len(self.pages) else Token(None)
        return self.pages[index], next_token


def page(prefix, moment, size=3):
    return [
        {
            "reviewId": f"{prefix}-{i}",
            "content": "kuota mahal",
            "score": 1,
            "thumbsUpCount": 0,
            "reviewCreatedVersion": "9.4.1",
            "at": moment - timedelta(minutes=i),
            "replyContent": None,
            "repliedAt": None,
        }
        for i in range(size)
    ]


def make_config(tmp_path, **overrides):
    raw = {
        "start_date": "2022-07-01",
        "batch_size": 3,
        "sleep_seconds": 0,
        "sleep_jitter": 0,
        "max_retries": 2,
        "backoff_base_seconds": 1.0,
        "checkpoint_every": 100,
        "output_dir": str(tmp_path),
        "apps": {"app": {"app_id": "com.example.app", "operator": "x", "group": "A"}},
    }
    raw.update(overrides)
    return ScraperConfig.model_validate(raw)


def make_scraper(tmp_path, fake, **overrides):
    sleeps = []
    scraper = PlayStoreScraper(
        make_config(tmp_path, **overrides), fetch=fake, sleep=sleeps.append, now=lambda: NOW
    )
    return scraper, sleeps


def three_pages():
    return [page("p0", RECENT), page("p1", IN_WINDOW), page("p2", TOO_OLD)]


def test_stops_at_start_date_and_drops_older_reviews(tmp_path):
    fake = FakePlayStore(three_pages())
    scraper, _ = make_scraper(tmp_path, fake)
    result = scraper.scrape_app("app")
    assert (result.reason, result.finished, result.scraped_count) == ("start_date", True, 6)
    assert fake.calls == [None, "t1", "t2"]
    assert ReviewStore(tmp_path, "app").row_count() == 6


def test_limit_stops_without_finishing_and_resume_continues(tmp_path):
    fake = FakePlayStore(three_pages())
    scraper, _ = make_scraper(tmp_path, fake)
    first = scraper.scrape_app("app", limit=3)
    assert (first.reason, first.finished) == ("limit", False)
    assert StateFile(ReviewStore(tmp_path, "app").state_path).load().next_token == "t1"

    second = scraper.scrape_app("app")
    assert second.reason == "start_date"
    assert fake.calls == [None, "t1", "t2"]
    assert ReviewStore(tmp_path, "app").row_count() == 6


def test_empty_token_is_retried_with_exponential_backoff(tmp_path):
    fake = FakePlayStore(three_pages(), fail_times=2)
    scraper, sleeps = make_scraper(tmp_path, fake)
    result = scraper.scrape_app("app")
    assert result.reason == "start_date"
    assert fake.calls[:3] == [None, None, None]
    assert [s for s in sleeps if s > 0] == [1.0, 2.0]


def test_persistent_failure_is_not_treated_as_finished_forever(tmp_path):
    fake = FakePlayStore(three_pages(), fail_times=100)
    scraper, _ = make_scraper(tmp_path, fake)
    failed = scraper.scrape_app("app")
    assert (failed.reason, failed.scraped_count) == ("exhausted_unverified", 0)
    assert len(fake.calls) == 3

    fake.fail_times = 0
    recovered = scraper.scrape_app("app")
    assert (recovered.reason, recovered.scraped_count) == ("start_date", 6)


def test_finished_app_is_skipped_on_next_run(tmp_path):
    fake = FakePlayStore(three_pages())
    scraper, _ = make_scraper(tmp_path, fake)
    scraper.scrape_app("app")
    calls_before = len(fake.calls)
    again = scraper.scrape_app("app")
    assert again.reason == "already_finished"
    assert len(fake.calls) == calls_before


def test_checkpoint_writes_multiple_chunks(tmp_path):
    pages = [page("p0", RECENT), page("p1", RECENT), page("p2", RECENT), page("p3", TOO_OLD)]
    fake = FakePlayStore(pages)
    scraper, _ = make_scraper(tmp_path, fake, checkpoint_every=4)
    scraper.scrape_app("app")
    store = ReviewStore(tmp_path, "app")
    assert len(store.parts()) == 2
    assert store.row_count() == 9


def test_saved_reviews_carry_source_metadata(tmp_path):
    fake = FakePlayStore(three_pages())
    scraper, _ = make_scraper(tmp_path, fake)
    scraper.scrape_app("app")
    table = pq.read_table(ReviewStore(tmp_path, "app").parts()[0])
    assert set(table.column("app_source").to_pylist()) == {"app"}
    assert set(table.column("sort_mode").to_pylist()) == {"newest"}
    assert table.column("scraped_at").to_pylist()[0] == NOW


def test_resume_token_carries_every_attribute_the_library_reads(tmp_path):
    fake = FakePlayStore(three_pages())
    scraper, _ = make_scraper(tmp_path, fake)
    scraper.scrape_app("app")
    resumed = fake.tokens[1]
    assert resumed.token == "t1"
    assert resumed.sort == Sort.NEWEST.value
    assert resumed.count == 3
    assert resumed.lang == "id"


def test_resume_token_matches_library_token_fields():
    from google_play_scraper.features.reviews import _ContinuationToken

    assert set(_ContinuationToken.__slots__) == {f.name for f in fields(ContinuationToken)}


def test_unknown_app_is_rejected(tmp_path):
    scraper, _ = make_scraper(tmp_path, FakePlayStore(three_pages()))
    with pytest.raises(KeyError):
        scraper.scrape_app("tidak-ada")


def test_last_page_with_data_is_not_retried(tmp_path):
    fake = FakePlayStore([page("p0", RECENT)])
    scraper, sleeps = make_scraper(tmp_path, fake)
    result = scraper.scrape_app("app")
    assert (result.reason, result.scraped_count) == ("exhausted_unverified", 3)
    assert fake.calls == [None]
    assert [s for s in sleeps if s > 0] == []
