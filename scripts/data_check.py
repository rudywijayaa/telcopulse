"""Pemeriksaan kualitas data mentah sebelum analisis."""

import sys
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"


def load(app: str) -> pd.DataFrame:
    files = sorted((RAW / app).glob("part-*.parquet"))
    if not files:
        raise SystemExit(f"Belum ada data untuk {app}")
    return pd.concat([pq.read_table(f).to_pandas() for f in files], ignore_index=True)


def main(app: str) -> None:
    df = load(app)
    total = len(df)
    local = df["reviewed_at"].dt.tz_convert("Asia/Jakarta").dt.tz_localize(None)
    quarters = local.dt.to_period("Q").astype(str)

    print(f"Aplikasi           : {app}")
    print(f"Jumlah ulasan      : {total}")
    print(f"Duplikat ID        : {df['review_id'].duplicated().sum()}")
    print(f"Tanggal terlama    : {df['reviewed_at'].min()}")
    print(f"Tanggal terbaru    : {df['reviewed_at'].max()}")
    print(f"app_version kosong : {df['app_version'].isna().mean():.1%}")
    print(f"Balasan developer  : {df['reply_content'].notna().sum()} dari {total}")
    print(f"Konten kosong      : {(df['content'].str.len() == 0).mean():.1%}")
    print("Distribusi rating  :")
    print(df["rating"].value_counts().sort_index().to_string())
    print("Ulasan per kuartal (WIB):")
    print(quarters.value_counts().sort_index().to_string())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Pakai: python scripts/data_check.py <app_source>")
    main(sys.argv[1])
