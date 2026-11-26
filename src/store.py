"""Penyimpanan ulasan ke Parquet per potongan kecil, plus posisi untuk melanjutkan scraping."""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from src.models import Review

TIMESTAMP = pa.timestamp("us", tz="UTC")

SCHEMA = pa.schema(
    [
        ("review_id", pa.string()),
        ("app_source", pa.string()),
        ("app_id", pa.string()),
        ("content", pa.string()),
        ("rating", pa.int8()),
        ("thumbs_up", pa.int32()),
        ("app_version", pa.string()),
        ("reviewed_at", TIMESTAMP),
        ("reply_content", pa.string()),
        ("replied_at", TIMESTAMP),
        ("sort_mode", pa.string()),
        ("scraped_at", TIMESTAMP),
    ]
)


class ReviewStore:
    def __init__(self, root: Path, app_source: str) -> None:
        self.directory = root / app_source
        self.directory.mkdir(parents=True, exist_ok=True)

    @property
    def state_path(self) -> Path:
        return self.directory / "state.json"

    def parts(self) -> list[Path]:
        return sorted(self.directory.glob("part-*.parquet"))

    def row_count(self) -> int:
        return sum(pq.ParquetFile(path).metadata.num_rows for path in self.parts())

    def write_chunk(self, reviews: list[Review]) -> Path | None:
        if not reviews:
            return None
        table = pa.Table.from_pylist([asdict(review) for review in reviews], schema=SCHEMA)
        path = self.directory / f"part-{self._next_index():05d}.parquet"
        # Tulis ke file sementara lalu ganti nama: crash di tengah tidak meninggalkan Parquet rusak.
        temp = path.with_suffix(".tmp")
        pq.write_table(table, temp)
        temp.replace(path)
        return path

    def _next_index(self) -> int:
        numbers = [int(path.stem.split("-")[1]) for path in self.parts()]
        return max(numbers, default=0) + 1


@dataclass
class ScrapeState:
    next_token: str | None = None
    scraped_count: int = 0
    oldest_seen: datetime | None = None
    finished: bool = False
    finish_reason: str | None = None


class StateFile:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> ScrapeState:
        if not self.path.exists():
            return ScrapeState()
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if raw["oldest_seen"] is not None:
            raw["oldest_seen"] = datetime.fromisoformat(raw["oldest_seen"])
        return ScrapeState(**raw)

    def save(self, state: ScrapeState) -> None:
        raw = asdict(state)
        raw["oldest_seen"] = state.oldest_seen.isoformat() if state.oldest_seen else None
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps(raw, indent=2), encoding="utf-8")
        temp.replace(self.path)
