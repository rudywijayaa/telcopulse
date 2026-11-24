"""Pengecekan metadata aplikasi Play Store."""

from dataclasses import dataclass
from datetime import date, datetime

from google_play_scraper import app, search
from google_play_scraper.exceptions import NotFoundError


@dataclass(frozen=True)
class AppInfo:
    """Data ringkas satu aplikasi."""

    app_id: str
    title: str
    developer: str
    rating: float | None
    ratings_count: int | None
    reviews_count: int | None
    version: str | None
    updated: date | None


@dataclass(frozen=True)
class SearchHit:
    """Satu hasil pencarian aplikasi."""

    app_id: str | None
    title: str
    developer: str


class AppChecker:
    """Mengambil informasi aplikasi dari Play Store."""

    def __init__(self, lang: str = "id", country: str = "id") -> None:
        self._lang = lang
        self._country = country

    def get_app(self, app_id: str) -> AppInfo | None:
        """Ambil detail aplikasi. Mengembalikan None jika ID tidak ditemukan."""
        try:
            raw = app(app_id, lang=self._lang, country=self._country)
        except NotFoundError:
            return None

        return AppInfo(
            app_id=app_id,
            title=raw["title"],
            developer=raw["developer"],
            rating=raw["score"],
            ratings_count=raw["ratings"],
            reviews_count=raw["reviews"],
            version=raw["version"],
            updated=self._to_date(raw["updated"]),
        )

    def search_apps(self, query: str, limit: int = 5) -> list[SearchHit]:
        """Cari aplikasi dari nama."""
        results = search(query, lang=self._lang, country=self._country, n_hits=limit)
        return [
            SearchHit(app_id=r["appId"], title=r["title"], developer=r["developer"])
            for r in results
        ]

    @staticmethod
    def _to_date(timestamp: int | None) -> date | None:
        """Ubah angka waktu (timestamp) menjadi tanggal."""
        if isinstance(timestamp, int):
            return datetime.fromtimestamp(timestamp).date()
        return None
