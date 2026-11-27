"""Pengambil ulasan Play Store: bertahap, bisa dilanjutkan, dan tahan error."""

import logging
import random
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from google_play_scraper import Sort, reviews

from src.config import ScraperConfig
from src.models import Review, review_from_raw
from src.store import ReviewStore, ScrapeState, StateFile

logger = logging.getLogger(__name__)

SORT_MODE = "newest"


@dataclass(frozen=True)
class ContinuationToken:
    """Meniru token internal library. reviews() hanya membaca atribut-atribut ini."""

    token: str | None
    lang: str
    country: str
    sort: int
    count: int
    filter_score_with: int | None = None
    filter_device_with: int | None = None


@dataclass(frozen=True)
class ScrapeResult:
    app_source: str
    scraped_count: int
    finished: bool
    reason: str


class PlayStoreScraper:
    def __init__(
        self,
        config: ScraperConfig,
        *,
        fetch: Callable[..., tuple[list[dict[str, Any]], Any]] = reviews,
        sleep: Callable[[float], None] = time.sleep,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._config = config
        self._fetch = fetch
        self._sleep = sleep
        self._now = now or (lambda: datetime.now(UTC))

    def scrape_apps(
        self, app_sources: Iterable[str], *, limit: int | None = None
    ) -> list[ScrapeResult]:
        return [self.scrape_app(name, limit=limit) for name in app_sources]

    def scrape_app(self, app_source: str, *, limit: int | None = None) -> ScrapeResult:
        app = self._config.apps[app_source]
        store = ReviewStore(self._config.output_dir, app_source)
        state_file = StateFile(store.state_path)
        state = state_file.load()
        if state.finished and state.finish_reason == "start_date":
            return ScrapeResult(app_source, state.scraped_count, True, "already_finished")

        cutoff = self._cutoff()
        buffer: list[Review] = []
        token_text = state.next_token

        while True:
            items, next_text = self._fetch_batch(app.app_id, token_text)
            batch = [
                review_from_raw(
                    raw,
                    app_source=app_source,
                    app_id=app.app_id,
                    sort_mode=SORT_MODE,
                    scraped_at=self._now(),
                )
                for raw in items
            ]
            kept = [review for review in batch if review.reviewed_at >= cutoff]
            buffer.extend(kept)
            self._update_counters(state, kept)

            reason = self._stop_reason(batch, kept, next_text, state, limit)
            if reason is None:
                token_text = next_text
                if len(buffer) >= self._config.checkpoint_every:
                    self._flush(app_source, store, state_file, state, buffer, token_text)
                    buffer = []
                self._pause()
                continue

            state.finished = reason != "limit"
            state.finish_reason = reason if state.finished else None
            resume_from = next_text if reason == "limit" else token_text
            self._flush(app_source, store, state_file, state, buffer, resume_from)
            return ScrapeResult(app_source, state.scraped_count, state.finished, reason)

    def _fetch_batch(
        self, app_id: str, token_text: str | None
    ) -> tuple[list[dict[str, Any]], str | None]:
        # reviews() menelan error dan mengembalikan hasil kosong dengan token kosong. Halaman
        # terakhir yang sah punya isi, jadi hanya respons kosong yang dicoba ulang.
        token = self._build_token(token_text)
        attempts = self._config.max_retries + 1
        for attempt in range(attempts):
            items, new_token = self._fetch(
                app_id,
                lang=self._config.language,
                country=self._config.country,
                sort=Sort.NEWEST,
                count=self._config.batch_size,
                continuation_token=token,
            )
            next_text = getattr(new_token, "token", None)
            if items or next_text is not None:
                return items, next_text
            if attempt < attempts - 1:
                logger.warning(
                    "%s: respons kosong, coba lagi %d dari %d", app_id, attempt + 1, attempts - 1
                )
                self._sleep(self._config.backoff_base_seconds * 2**attempt)
        return items, None

    def _build_token(self, token_text: str | None) -> ContinuationToken | None:
        if token_text is None:
            return None
        return ContinuationToken(
            token=token_text,
            lang=self._config.language,
            country=self._config.country,
            sort=Sort.NEWEST.value,
            count=self._config.batch_size,
        )

    def _cutoff(self) -> datetime:
        # Mundur sehari: kuartal dihitung di WIB (UTC+7), jadi ambil sedikit berlebih lalu saring.
        start = self._config.start_date
        return datetime(start.year, start.month, start.day, tzinfo=UTC) - timedelta(days=1)

    def _pause(self) -> None:
        self._sleep(self._config.sleep_seconds + random.uniform(0, self._config.sleep_jitter))

    @staticmethod
    def _update_counters(state: ScrapeState, kept: list[Review]) -> None:
        if not kept:
            return
        state.scraped_count += len(kept)
        oldest = min(review.reviewed_at for review in kept)
        if state.oldest_seen is None or oldest < state.oldest_seen:
            state.oldest_seen = oldest

    @staticmethod
    def _stop_reason(
        batch: list[Review],
        kept: list[Review],
        next_text: str | None,
        state: ScrapeState,
        limit: int | None,
    ) -> str | None:
        if batch and not kept:
            return "start_date"
        if next_text is None or not batch:
            return "exhausted_unverified"
        if limit is not None and state.scraped_count >= limit:
            return "limit"
        return None

    @staticmethod
    def _flush(
        app_source: str,
        store: ReviewStore,
        state_file: StateFile,
        state: ScrapeState,
        buffer: list[Review],
        next_token: str | None,
    ) -> None:
        # Data ditulis dulu, baru posisi disimpan: crash di antaranya hanya menghasilkan duplikat.
        store.write_chunk(buffer)
        state.next_token = next_token
        state_file.save(state)
        logger.info(
            "%s: %d ulasan tersimpan, tertua %s", app_source, state.scraped_count, state.oldest_seen
        )
