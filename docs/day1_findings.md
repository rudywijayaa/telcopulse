# Temuan Hari 1

Tanggal cek: 2026-11-24. Sumber: `python scripts/check_apps.py` (Play Store, toko Indonesia).

## ID aplikasi

| Operator  | Aplikasi    | ID                        | Developer                 | Perkiraan ulasan | Catatan                                 |
| --------- | ----------- | ------------------------- | ------------------------- | ---------------- | --------------------------------------- |
| Telkomsel | MyTelkomsel | com.telkomsel.telkomselcm | Telkomsel                 | 2,95 juta        | Aktif                                   |
| Indosat   | myIM3       | com.pure.indosat.care     | Indosat Ooredoo Hutchison | 2,82 juta        | Aktif                                   |
| Indosat   | Bima+ (Tri) | com.linkit.bimatri        | Indosat Ooredoo Hutchison | 644 ribu         | Aplikasi merek Tri, terpisah dari myIM3 |
| XL        | myXL        | com.apps.MyXL             | XLSMART                   | 1,08 juta        | Analisis sekunder, pra-merger saja      |

Angka ulasan adalah perkiraan dari Play Store dan berubah antar pengecekan. Jumlah yang benar-benar bisa diambil ditentukan saat scraping.

## Keputusan

1. **Pembanding utama:** Telkomsel vs Indosat.
2. **Aplikasi Indosat:** myIM3 dan Bima+ keduanya diambil, dibedakan dengan kolom `app_source`. Analisis utama memakai gabungan, uji ketahanan memakai myIM3 saja.
3. **XL:** sekunder, pra-merger. Developer aplikasi kini XLSMART.
4. **Hasil pencarian Play Store** kadang mengembalikan ID kosong (`None`). ID hanya diambil dari `get_app`.

## Yang masih harus diverifikasi

- [ ] ARPU Indosat di laporan keuangan mencakup merek IM3 dan Tri.
- [ ] ARPU Telkomsel mencakup by.U, dan apakah by.U punya aplikasi sendiri (cek ID).
- [ ] Definisi ARPU dan pelanggan sama antar operator.
- [ ] Persentase `appVersion` terisi di ulasan (cek setelah scraper jadi).
