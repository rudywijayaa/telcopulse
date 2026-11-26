from datetime import UTC, datetime, timedelta, timezone

import pytest

from src.models import review_from_raw

SCRAPED_AT = datetime(2026, 11, 26, 8, 0, tzinfo=UTC)
JAKARTA = timezone(timedelta(hours=7))


def raw_review(**overrides):
    raw = {
        "reviewId": "gp:abc123",
        "content": "kuota mahal sekali",
        "score": 1,
        "thumbsUpCount": 4,
        "reviewCreatedVersion": "9.4.1",
        "at": datetime(2025, 4, 1, 7, 30, tzinfo=JAKARTA),
        "replyContent": None,
        "repliedAt": None,
    }
    raw.update(overrides)
    return raw


def convert(raw):
    return review_from_raw(
        raw,
        app_source="mytelkomsel",
        app_id="com.telkomsel.telkomselcm",
        sort_mode="newest",
        scraped_at=SCRAPED_AT,
    )


def test_maps_basic_fields():
    review = convert(raw_review())
    assert review.review_id == "gp:abc123"
    assert review.app_source == "mytelkomsel"
    assert review.rating == 1
    assert review.thumbs_up == 4
    assert review.app_version == "9.4.1"
    assert review.sort_mode == "newest"


def test_review_time_is_converted_to_utc():
    review = convert(raw_review())
    assert review.reviewed_at == datetime(2025, 4, 1, 0, 30, tzinfo=UTC)
    assert review.reviewed_at.utcoffset() == timedelta(0)


def test_naive_datetime_becomes_timezone_aware():
    review = convert(raw_review(at=datetime(2025, 4, 1, 7, 30)))
    assert review.reviewed_at.tzinfo is not None
    assert review.reviewed_at.utcoffset() == timedelta(0)


def test_empty_content_becomes_empty_string():
    assert convert(raw_review(content=None)).content == ""


def test_app_version_falls_back_to_app_version_key():
    raw = raw_review(reviewCreatedVersion=None, appVersion="9.3.0")
    assert convert(raw).app_version == "9.3.0"


def test_missing_app_version_is_none():
    assert convert(raw_review(reviewCreatedVersion=None)).app_version is None


def test_reply_fields_are_mapped_when_present():
    replied = datetime(2025, 4, 2, 9, 0, tzinfo=JAKARTA)
    review = convert(raw_review(replyContent="Terima kasih", repliedAt=replied))
    assert review.reply_content == "Terima kasih"
    assert review.replied_at == datetime(2025, 4, 2, 2, 0, tzinfo=UTC)


def test_schema_drift_fails_loudly():
    raw = raw_review()
    del raw["reviewId"]
    with pytest.raises(KeyError):
        convert(raw)
