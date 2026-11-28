# Temuan Hari 1 (dan catatan hari 2 yang menyusul)

Tanggal cek ID: 2026-11-25. Sumber aplikasi: `python scripts/check_apps.py` (Play Store, toko Indonesia). Sumber keuangan: dokumen perusahaan yang tercatat per baris di CSV.

Dokumen ini dibagi dua bagian: **Hari 1** (keputusan desain dan verifikasi) dan **Hari 2** (hasil scraping dan pemeriksaan kualitas). Hari 2 dicatat di sini karena scraping dijalankan setelah keputusan hari 1 selesai.

---

## Hari 1: keputusan dan verifikasi

### Pertanyaan riset (terkunci)

Penjelasan mana yang paling konsisten dengan waktu, segmen, dan pola lintas operator dari penyusutan basis pelanggan Telkomsel dari puncak 2024-Q2 (159,9 juta) sampai 2026-Q3 (151,1 juta)? Pelanggan berarti kartu SIM tercatat, bukan orang unik.

### ID aplikasi (terverifikasi `get_app`, 2026-11-25)

| Kelompok | Operator  | Aplikasi                                    | ID                        | Developer                  | Perkiraan ulasan | Catatan                                    |
| -------- | --------- | ------------------------------------------- | ------------------------- | -------------------------- | ---------------- | ------------------------------------------ |
| A        | Telkomsel | MyTelkomsel                                 | com.telkomsel.telkomselcm | Telkomsel                  | 2.951.446        | Sejak 2023-Q3 juga melayani IndiHome       |
| A        | Telkomsel | by.U                                        | com.byu.id                | by.U                       | 306.383          | Merek digital Telkomsel                    |
| A        | Indosat   | myIM3                                       | com.pure.indosat.care     | Indosat Ooredoo Hutchison  | 2.824.870        | Merek IM3                                  |
| A        | Indosat   | Bima+ (Tri)                                 | com.linkit.bimatri        | Indosat Ooredoo Hutchison. | 644.507          | Merek Tri, terpisah dari myIM3             |
| B        | XL        | myXL                                        | com.apps.MyXL             | XLSMART                    | 1.075.986        | Replikasi pra-merger saja                  |
| B        | XL        | AXISnet                                     | com.axis.net              | AXIS.                      | 1.351.793        | Replikasi pra-merger saja                  |
| C        | XLSMART   | mySmartfren (judul kini "mySF. #AppJagoan") | com.smartfren             | Smartfren.                 | 667.065          | Ditunda, hanya pasca-merger dan deskriptif |

Angka ulasan adalah batas atas kasar dari Play Store dan berubah antar pengecekan. Jumlah yang benar-benar tersedia ditentukan saat scraping. Pencocokan data selalu lewat `app_id`, bukan nama developer (nama developer tidak konsisten, misalnya titik di akhir).

### Data keuangan kuartalan

| File                     | Operator     | Kuartal             | Catatan                                           |
| ------------------------ | ------------ | ------------------- | ------------------------------------------------- |
| telkomsel_quarterly.csv  | Telkomsel    | 2022-Q3 s/d 2026-Q3 | 17 kuartal, tanpa gap. Sudah memuat dua koreksi   |
| indosat_quarterly.csv    | Indosat      | 2022-Q3 s/d 2026-Q3 | 17 kuartal, tanpa gap                             |
| xl_xlsmart_quarterly.csv | XL / XLSMART | 2022-Q3 s/d 2026-Q3 | Sebelum 2025-Q2 = XL (+AXIS), sesudahnya gabungan |

File dari Excel memakai pemisah titik koma. Sudah distandarkan ke koma dan UTF-8 di `data/reference/`.

### Keputusan

1. **Fokus:** Telkomsel kasus utama, Indosat pembanding utama. XL hanya replikasi pra-merger (2022-Q3 s/d 2025-Q1, 11 kuartal). XL pasca-merger (7 kuartal) deskriptif saja, karena data keuangan XL, AXIS, dan Smartfren tidak dipisahkan per merek.
2. **Aplikasi:** Kelompok A diambil lebih dulu. Analisis utama memakai gabungan per operator, uji ketahanan membuang aplikasi kedua (by.U atau Bima+).
3. **by.U:** manajemen menyebut sekitar 20 juta pelanggan (Sep 2026), sekitar 13% basis Telkomsel. Itu klaim manajemen, dan belum terkonfirmasi apakah termasuk dalam 151,1 juta. Pernyataan "lebih dari 97% pelanggan memakai MyTelkomsel" tidak dipakai.
4. **Kelompok C:** mySmartfren ditunda, hanya untuk jendela pasca-merger dan deskriptif.
5. **ID aplikasi** hanya diambil dari `get_app`. Hasil pencarian Play Store kadang mengembalikan ID kosong (`None`).
6. **Ukuran pendapatan seluler Telkomsel:** `mobile_service_rev`, bukan total revenue, karena total melompat di 2023-Q3 akibat integrasi IndiHome.

### Koreksi data keuangan

- Telkomsel `mobile_service_rev` 2025-Q1: 20.576 menjadi 20.546. Yield menjadi 3,64.
- Telkomsel `mobile_service_rev` 2026-Q1: 21.147 menjadi 21.217. Yield menjadi 3,68.
- Setelah koreksi, 9M25 = 61.603 dan 9M26 = 63.758, sama dengan dokumen sumber.
- Selisih prabayar + pascabayar dengan total (±1 ribu Telkomsel, ±100 ribu Indosat) adalah pembulatan.
- Sekitar 88% penurunan Telkomsel dari puncaknya terjadi setelah 2025-Q1. Rentang ini ditemukan setelah melihat data, jadi berstatus **eksploratif**, bukan hipotesis awal.

### Checklist verifikasi

- [x] ID by.U, AXISnet, dan mySmartfren lewat `get_app` (2026-11-25).
- [ ] Apakah 151,1 juta pelanggan Telkomsel sudah memuat by.U.
- [ ] ARPU Indosat mencakup merek IM3 dan Tri.
- [ ] ARPU Indosat 2026-Q1: 45.200 (tabel) vs 45.000 (narasi). Konfirmasi di memo 1Q26.
- [ ] Satuan payload: Telkomsel dari TB dibagi 1.024. Cek satuan Indosat, lalu seragamkan.
- [ ] Anomali Telkomsel 2023-Q4 (legacy turun 52% QoQ lalu naik 58%): cek memo FY23.
- [ ] Persentase `app_version` kosong per kuartal (lihat Hari 2).
- [ ] Kumpulkan `events.csv`, Google Trends mingguan, dan indikator makro.

---

## Hari 2: scraping dan kualitas data (2026-11-27 sampai 2026-11-28)

### Uji coba (2.000 ulasan per aplikasi)

Dijalankan untuk menguji pipeline. **Hasilnya tidak dipakai sebagai angka resmi**, karena hanya mengambil ulasan terbaru (sekitar 9 hari).

- Bima+: 2.000 ulasan, `alasan=limit`, ulasan tertua 2026-11-06.
- MyTelkomsel: 2.000 ulasan, `alasan=limit`, ulasan tertua 2026-11-17.
- Duplikat ID: 0. Konten kosong: 0%.

### Scraping penuh MyTelkomsel (2026-11-27)

Dijalankan dengan `python scripts/scrape.py --apps mytelkomsel`.

- Total ulasan tersimpan: **737.099**, dalam 149 part Parquet (part 1 uji coba 2.000, part 2 sampai 148 berisi 5.000, part 149 berisi 99).
- Berhenti dengan `selesai=True, alasan=start_date`. Ulasan tertua 2022-06-30 00:00 UTC.
- Duplikat ID: **0**. Konten kosong: **0%**.
- Ulasan sebelum 1 Juli 2022 WIB (sebelum 2022-06-30 17:00 UTC): **1.304**. Ini dibuang di tahap pembersihan, data mentah tidak diubah.
- Kuartal dihitung di Asia/Jakarta (WIB). 2026Q4 hanya berisi ulasan sampai 26 November, jadi belum lengkap dan tidak dipakai untuk perbandingan.

Sebaran per kuartal (WIB), data mentah sebelum pembersihan:

| Kuartal | Ulasan | Kuartal | Ulasan                 |
| ------- | ------ | ------- | ---------------------- |
| 2022Q2  | 1.304  | 2024Q3  | 34.062                 |
| 2022Q3  | 86.935 | 2024Q4  | 54.549                 |
| 2022Q4  | 63.059 | 2025Q1  | 50.182                 |
| 2023Q1  | 30.956 | 2025Q2  | 43.789                 |
| 2023Q2  | 27.467 | 2025Q3  | 44.685                 |
| 2023Q3  | 43.406 | 2025Q4  | 41.377                 |
| 2023Q4  | 40.081 | 2026Q1  | 37.388                 |
| 2024Q1  | 28.808 | 2026Q2  | 31.740                 |
| 2024Q2  | 37.673 | 2026Q3  | 26.436                 |
|         |        | 2026Q4  | 13.202 (belum lengkap) |

Distribusi rating (seluruh data): 1: 341.513, 2: 48.759, 3: 41.832, 4: 43.728, 5: 261.267.

### Kelengkapan kolom MyTelkomsel

- `app_version` kosong: **19,1%** (seluruh data). Angka uji coba 20,3% tidak mewakili.
- Balasan developer: **522.910 dari 737.099 (71%)**. Angka uji coba 1.999 dari 2.000 tidak mewakili. Balasan berupa templat layanan pelanggan (mengarahkan ke email dan Call Center 188), jadi tidak dipakai sebagai sinyal sentimen.

### Scraping penuh by.U (2026-11-28)

- Total ulasan: **152.866**, 2022-06-30 sampai 2026-11-27, `selesai=True, alasan=start_date`.
- Duplikat ID: 0. Konten kosong: 0%.
- `app_version` kosong: 18,6%.
- Balasan developer: 147.281 (96,3%), templat layanan, tidak dipakai sebagai sinyal sentimen.
- Distribusi rating: 1: 62.649, 2: 11.502, 3: 11.145, 4: 10.440, 5: 57.130.
- Estimasi awal dari `check_apps` (306 ribu) adalah total sepanjang masa. Yang diambil sejak 2022-07-01 lebih kecil.
- Sebaran kuartal (WIB) by.U:

| Kuartal | Ulasan | Kuartal | Ulasan                |
| ------- | ------ | ------- | --------------------- |
| 2022Q2  | 82     | 2024Q4  | 9.916                 |
| 2022Q3  | 6.655  | 2025Q1  | 9.013                 |
| 2022Q4  | 8.055  | 2025Q2  | 11.610                |
| 2023Q1  | 4.295  | 2025Q3  | 11.356                |
| 2023Q2  | 3.759  | 2025Q4  | 14.779                |
| 2023Q3  | 3.619  | 2026Q1  | 16.606                |
| 2023Q4  | 7.874  | 2026Q2  | 8.176                 |
| 2024Q1  | 7.253  | 2026Q3  | 10.357                |
| 2024Q2  | 6.359  |         |                       |
| 2024Q3  | 8.193  | 2026Q4  | 4.909 (belum lengkap) |

- Penurunan 2026Q2 (8.176) dibanding 2026Q1 (16.606) belum diinterpretasikan. Bandingkan dengan MyTelkomsel pada kuartal yang sama sebelum menyimpulkan apa pun.

### Yang belum diperiksa

- Persentase `app_version` kosong dan balasan per kuartal, untuk menentukan apakah H6 harus dibatasi ke periode tertentu: **(isi setelah pemeriksaan per kuartal)**.
- Scraping myIM3 dan Bima+ penuh: **belum dilakukan**.
- Perbandingan sebaran kuartal by.U dengan MyTelkomsel: **belum dilakukan**.
