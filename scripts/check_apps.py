"""Cek ID aplikasi Play Store. Jalankan: python scripts/check_apps.py"""

from src.app_checker import AppChecker, AppInfo

KNOWN_IDS = {
    "telkomsel": "com.telkomsel.telkomselcm",
    "indosat_myim3": "com.pure.indosat.care",
    "indosat_bima": "com.linkit.bimatri",
    "xl": "com.apps.MyXL",
}
SEARCH_QUERIES = ["myIM3", "Bima+ Tri"]


def print_app(label: str, app_id: str, info: AppInfo | None) -> None:
    if info is None:
        print(f"[{label}] TIDAK DITEMUKAN: {app_id}")
        return

    print(f"[{label}] {info.title} | {info.app_id}")
    print(f"  developer={info.developer}")
    print(
        f"  rating={info.rating} ratings={info.ratings_count} "
        f"reviews={info.reviews_count}"
    )
    print(f"  version={info.version} updated={info.updated}")


def main() -> None:
    checker = AppChecker()

    for label, app_id in KNOWN_IDS.items():
        print_app(label, app_id, checker.get_app(app_id))

    for query in SEARCH_QUERIES:
        print(f"\nSearch: {query}")
        for hit in checker.search_apps(query):
            print(f"  {hit.title} | {hit.app_id} | {hit.developer}")


if __name__ == "__main__":
    main()
