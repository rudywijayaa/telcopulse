import argparse
import logging
import sys
from pathlib import Path

from src.config import load_config
from src.scraper import PlayStoreScraper

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs" / "scraper.yaml"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape ulasan Play Store.")
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--groups", help="kelompok dipisah koma, misalnya A atau A,B")
    selection.add_argument("--apps", help="nama aplikasi dipisah koma, misalnya mytelkomsel,byu")
    parser.add_argument(
        "--limit", type=int, default=None, help="berhenti setelah N ulasan per aplikasi"
    )
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser.parse_args(argv)


def select_apps(config, args: argparse.Namespace) -> list[str]:
    if args.apps:
        names = [name.strip() for name in args.apps.split(",") if name.strip()]
        unknown = [name for name in names if name not in config.apps]
        if unknown:
            raise SystemExit(f"Aplikasi tidak dikenal di config: {', '.join(unknown)}")
        return names
    groups = [group.strip() for group in args.groups.split(",") if group.strip()]
    return list(config.apps_in_groups(*groups))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    config = load_config(args.config)
    names = select_apps(config, args)
    if not names:
        raise SystemExit("Tidak ada aplikasi yang cocok dengan pilihan.")

    scraper = PlayStoreScraper(config)
    for result in scraper.scrape_apps(names, limit=args.limit):
        print(
            f"{result.app_source}: {result.scraped_count} ulasan, "
            f"selesai={result.finished}, alasan={result.reason}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
