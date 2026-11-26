"""Bentuk satu ulasan dan pemetaannya dari data mentah google-play-scraper."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class Review:
    review_id: str
    app_source: str
    app_id: str
    content: str
    rating: int
    thumbs_up: int
    app_version: str | None
    reviewed_at: datetime
    reply_content: str | None
    replied_at: datetime | None
    sort_mode: str
    scraped_at: datetime


def _to_utc(moment: datetime) -> datetime:
    # Datetime tanpa zona dianggap waktu lokal mesin, jadi hasilnya sama di laptop dan Kaggle.
    return moment.astimezone(UTC)


def review_from_raw(
    raw: dict[str, Any],
    *,
    app_source: str,
    app_id: str,
    sort_mode: str,
    scraped_at: datetime,
) -> Review:
    replied_at = raw.get("repliedAt")
    return Review(
        review_id=raw["reviewId"],
        app_source=app_source,
        app_id=app_id,
        content=raw["content"] or "",
        rating=raw["score"],
        thumbs_up=raw["thumbsUpCount"],
        app_version=raw.get("reviewCreatedVersion") or raw.get("appVersion"),
        reviewed_at=_to_utc(raw["at"]),
        reply_content=raw.get("replyContent"),
        replied_at=_to_utc(replied_at) if replied_at else None,
        sort_mode=sort_mode,
        scraped_at=scraped_at,
    )
