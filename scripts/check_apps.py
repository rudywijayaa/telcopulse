"""Cek ID aplikasi Play Store. Jalankan: python scripts/check_apps.py"""

from src.app_checker import AppChecker, AppInfo

# Nama kunci = nilai app_source yang nanti dipakai scraper.
KNOWN_IDS = {
    # Kelompok A: inti analisis
    "mytelkomsel": "com.telkomsel.telkomselcm",
    "byu": "com.byu.id",
    "myim3": "com.pure.indosat.care",
    "bimaplus": "com.linkit.bimatri",
    # Kelompok B: replikasi pra-merger
    "myxl": "com.apps.MyXL",
    "axisnet": "com.axis.net",
    # Kelompok C: ditunda, ID belum diverifikasi
    "mysmartfren": "com.smartfren",
}
SEARCH_QUERIES = ["by.U", "mySmartfren"]


def print_app(label: str, app_id: str, info: AppInfo | None) -> None:
    if info is None:
        print(f"[{label}] TIDAK DITEMUKAN: {app_id}")
        return

    print(f"[{label}] {info.title} | {info.app_id}")
    print(f"  developer={info.developer}")
    print(f"  rating={info.rating} ratings={info.ratings_count} reviews={info.reviews_count}")
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
