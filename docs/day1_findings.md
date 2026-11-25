# Temuan Hari 1

Tanggal cek: 2026-11-25. Sumber aplikasi: `python scripts/check_apps.py` (Play Store, toko Indonesia). Sumber keuangan: dokumen perusahaan yang tercatat per baris di CSV.

## Pertanyaan riset (terkunci)

Penjelasan mana yang paling konsisten dengan waktu, segmen, dan pola lintas operator dari penyusutan basis pelanggan Telkomsel dari puncak 2024-Q2 (159,9 juta) sampai 2026-Q3 (151,1 juta)? Pelanggan berarti kartu SIM tercatat, bukan orang unik.

## ID aplikasi (semua terverifikasi dengan get_app, 2026-11-25)

| Kelompok | Operator  | Aplikasi                                    | ID                        | Developer                  | Perkiraan ulasan | Catatan                                    |
| -------- | --------- | ------------------------------------------- | ------------------------- | -------------------------- | ---------------- | ------------------------------------------ |
| A        | Telkomsel | MyTelkomsel                                 | com.telkomsel.telkomselcm | Telkomsel                  | 2.951.446        | Sejak 2023-Q3 juga melayani IndiHome       |
| A        | Telkomsel | by.U                                        | com.byu.id                | by.U                       | 306.383          | Merek digital Telkomsel                    |
| A        | Indosat   | myIM3                                       | com.pure.indosat.care     | Indosat Ooredoo Hutchison  | 2.824.870        | Merek IM3                                  |
| A        | Indosat   | Bima+ (Tri)                                 | com.linkit.bimatri        | Indosat Ooredoo Hutchison. | 644.507          | Merek Tri, terpisah dari myIM3             |
| B        | XL        | myXL                                        | com.apps.MyXL             | XLSMART                    | 1.075.986        | Replikasi pra-merger saja                  |
| B        | XL        | AXISnet                                     | com.axis.net              | AXIS.                      | 1.351.793        | Replikasi pra-merger saja                  |
| C        | XLSMART   | mySmartfren (judul kini "mySF. #AppJagoan") | com.smartfren             | Smartfren.                 | 667.065          | Ditunda, hanya pasca-merger dan deskriptif |

Jumlah ulasan sepanjang masa: Kelompok A 6.727.206, Kelompok B 2.427.779, Kelompok C 667.065 (total 9.822.050). Angka berubah antar pengecekan dan hanya batas atas kasar. Jumlah sejak 2022-07-01 harus dihitung saat scraping.

Catatan: nama developer tidak konsisten (titik di akhir "Indosat Ooredoo Hutchison.", "AXIS.", "Smartfren."). Pencocokan data selalu lewat `app_id`, bukan nama developer.

## Data keuangan kuartalan

| File                                | Operator     | Kuartal             | Catatan                                           |
| ----------------------------------- | ------------ | ------------------- | ------------------------------------------------- |
| telkomsel_quarterly_final_v2.csv    | Telkomsel    | 2022-Q3 s/d 2026-Q3 | 17 kuartal, tanpa gap. Sudah memuat dua koreksi   |
| indosat_quarterly_final_1.csv       | Indosat      | 2022-Q3 s/d 2026-Q3 | 17 kuartal, tanpa gap                             |
| xlsmart_quarterly_2022q1_2026q3.csv | XL / XLSMART | 2022-Q3 s/d 2026-Q3 | Sebelum 2025-Q2 = XL (+AXIS), sesudahnya gabungan |

File dari Excel memakai pemisah titik koma. Standarkan ke koma dan UTF-8 sebelum masuk `data/reference/`.

## Keputusan

1. **Fokus:** Telkomsel kasus utama, Indosat pembanding utama. XL hanya replikasi pra-merger (2022-Q3 s/d 2025-Q1, 11 kuartal). XL pasca-merger (7 kuartal) deskriptif saja, karena data keuangan XL, AXIS, dan Smartfren tidak dipisahkan per merek.
2. **Aplikasi:** Kelompok A discrape lebih dulu: MyTelkomsel + by.U dan myIM3 + Bima+, dibedakan dengan kolom `app_source`. Analisis utama memakai gabungan per operator, uji ketahanan membuang aplikasi kedua (by.U atau Bima+).
3. **by.U:** manajemen menyebut sekitar 20 juta pelanggan (Sep 2026), atau sekitar 13% basis Telkomsel. Angka lama 3 sampai 4 juta (2022) tidak dipakai. Itu klaim manajemen, dan belum terkonfirmasi apakah termasuk dalam 151,1 juta. Pernyataan ">97% pelanggan memakai MyTelkomsel" tidak boleh dipakai. Ulasan by.U sepanjang masa sekitar 9,4% dari gabungan ulasan Telkomsel (306 ribu dari 3,26 juta).
4. **Kelompok C:** mySmartfren ditunda, hanya untuk jendela pasca-merger dan deskriptif.
5. **ID aplikasi** hanya diambil dari `get_app`. Hasil pencarian Play Store selalu mengembalikan ID kosong (`None`) pada hasil teratas.
6. **Ukuran pendapatan seluler Telkomsel:** `mobile_service_rev`, bukan total revenue, karena total melompat di 2023-Q3 akibat integrasi IndiHome.

## Koreksi dan temuan data

- Telkomsel `mobile_service_rev` 2025-Q1: 20.576 menjadi 20.546 (legacy 1.992 + digital 18.554). Yield menjadi 3,64.
- Telkomsel `mobile_service_rev` 2026-Q1: 21.147 menjadi 21.217 (legacy 1.026 + digital 20.191). Yield menjadi 3,68.
- Setelah koreksi, jumlah 9M25 = 61.603 dan 9M26 = 63.758, sama dengan dokumen.
- Selisih prabayar + pascabayar dengan total (±1 ribu Telkomsel, ±100 ribu Indosat) adalah pembulatan.
- Sekitar 88% penurunan Telkomsel dari puncaknya terjadi setelah 2025-Q1. Rentang ini ditemukan setelah melihat data, jadi berstatus eksploratif.

## Yang masih harus diverifikasi

- [x] ID by.U, AXISnet, dan mySmartfren lewat `get_app` (2026-11-25).
- [ ] Apakah 151,1 juta pelanggan Telkomsel sudah memuat by.U.
- [ ] ARPU Indosat mencakup merek IM3 dan Tri.
- [ ] ARPU Indosat 2026-Q1: 45.200 (tabel) vs 45.000 (narasi). Konfirmasi di memo 1Q26.
- [ ] Satuan payload: Telkomsel dari TB dibagi 1.024. Cek satuan Indosat, lalu seragamkan.
- [ ] Anomali Telkomsel 2023-Q4 (legacy turun 52% QoQ lalu naik 58%): cek memo FY23.
- [ ] Jumlah ulasan per kuartal sejak 2022-07-01 dan persentase `appVersion` terisi (setelah scraper jadi).
- [ ] Kumpulkan `events.csv`, Google Trends mingguan, dan indikator makro.
