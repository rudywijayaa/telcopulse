# PRD TelcoPulse v3: Basis Pelanggan Telkomsel Menyusut ±8,8 Juta: Harga, Pembersihan Basis, atau Daya Beli?

Versi 3.0, pertanyaan riset diperbarui 25 November 2026 | Durasi: 4 minggu | Peran target: Data Analyst (utama), Data Scientist, ML Engineer

## 1. Ringkasan Eksekutif

TelcoPulse menguji penjelasan yang bersaing atas penyusutan basis pelanggan seluler Telkomsel dari puncak 2024-Q2 (159,9 juta) ke 2026-Q3 (151,1 juta), atau sekitar 8,8 juta kartu SIM tercatat (turun 5,5%). Alatnya: data keuangan kuartalan tiga operator, sinyal keluhan mingguan dari ulasan Play Store, dan Indosat sebagai pembanding utama.

Tiga penjelasan utama diuji: kenaikan harga efektif kuota, pembersihan basis pelanggan yang disengaja, dan melemahnya daya beli. Persaingan dan merger serta kualitas layanan diuji sebagai penjelasan tambahan. Setiap penjelasan punya jejak data yang diprediksi, ditulis dan dikunci sebelum analisis (Bagian 3.2). Kesimpulan ditulis sebagai konsisten atau tidak konsisten dengan, bukan sebab-akibat, karena churn kotor dan alasan berhenti tidak tersedia publik.

Ulasan Play Store berperan sebagai sensor keluhan mingguan, bukan sebagai jawaban. Sistem klasifikasi sentimen dan topik, API, dashboard, dan CI/CD tetap dibangun sebagai instrumen pengukur dan produk teknis. Prinsip proyek: kedalaman lebih penting daripada lebar, dan setiap klaim harus didukung evaluasi.

## 2. Latar Belakang dan Masalah Bisnis

Konten media sosial menyebut pelanggan Telkomsel turun hingga jutaan dan menyalahkan kenaikan harga kuota. Data resmi memang menunjukkan penurunan, tetapi tiga temuan awal membuat satu penjelasan tunggal berisiko:

1. Ketiga operator menyusut. Dari puncaknya: Telkomsel turun 5,5% (2024-Q2), Indosat 10,5% (2022-Q4), XLSMART 15,3% (2025-Q2, terdistorsi merger). Penurunan Telkomsel justru yang paling kecil secara proporsi.
2. ARPU Telkomsel hampir datar (Rp45.000 di 2022-Q3, Rp44.900 di 2026-Q3) sementara ARPU Indosat naik 33,3%. Manajemen menyebut pengelolaan kualitas basis, jadi sebagian penurunan bisa disengaja.
3. Sekitar 88% penurunan Telkomsel dari puncaknya terjadi setelah 2025-Q1, bersamaan dengan penyederhanaan starter pack (Mar 2025) dan konsolidasi XL-Smartfren (Apr-Mei 2025). Rentang waktu ini dipilih setelah melihat data, jadi berstatus eksploratif.

Pelanggan di sini berarti kartu SIM tercatat, bukan orang unik. Sebagian penurunan bisa berasal dari pembersihan kartu tidak aktif.

## 3. Tujuan, Hipotesis, dan Metrik Keberhasilan

### 3.1 Pertanyaan riset (Data Analyst)

Pertanyaan riset: penjelasan mana yang paling konsisten dengan waktu, segmen, dan pola lintas operator dari penyusutan basis pelanggan Telkomsel dari puncak 2024-Q2 sampai 2026-Q3? Telkomsel adalah kasus utama, Indosat pembanding utama, dan XL replikasi sekunder pra-merger. Proyek tidak mengklaim kausalitas. Kesimpulan ditulis sebagai konsisten atau tidak konsisten dengan, disertai interval kepercayaan dan batas yang jelas.

### 3.2 Penjelasan yang diuji dan prediksinya (dikunci sebelum analisis)

| Kode | Penjelasan | Jejak yang diprediksi di data | Yang akan membantahnya |
| --- | --- | --- | --- |
| H1 | Harga efektif naik | Yield (Rp per MB) naik; porsi ulasan berkeluhan harga naik sebelum pelanggan turun; penurunan terpusat di prabayar | Keluhan harga tidak mendahului penurunan; penurunan merata di pascabayar |
| H2 | Pembersihan basis disengaja | ARPU dan payload per pelanggan naik saat pelanggan turun, tanpa lonjakan keluhan | Pelanggan turun bersamaan dengan ARPU turun |
| H3 | Daya beli melemah | Penurunan serentak di semua operator dan searah dengan indeks keyakinan konsumen dan penjualan ritel | Operator turun pada waktu berbeda tanpa kaitan makro |
| H4 | Persaingan dan merger | Pergeseran bertepatan dengan event kompetitor di events.csv | Tidak ada kaitan waktu dengan event |
| H5 | Kualitas jaringan atau aplikasi | Porsi keluhan sinyal dan bug naik sebelum penurunan | Keluhan sinyal dan bug tetap atau baru naik setelah penurunan |
| H6 | Deteksi dini (sistem) | Rilis versi besar diikuti lonjakan keluhan bug dalam 14 hari, terdeteksi sebelum rating turun | Tidak ada lonjakan, atau terdeteksi setelah rating turun |

Aturan: tabel ini dikunci dengan commit Git sebelum hasil analisis dilihat. Kontrol negatif: keluhan topik bug tidak boleh memprediksi perubahan pelanggan dengan pola yang sama seperti keluhan harga. Beberapa penjelasan dapat berlaku bersamaan, jadi hasil dilaporkan sebagai kontribusi relatif, dan hasil nol dilaporkan sebagai temuan sah.

Catatan: satuan payload (PB) belum diseragamkan antar operator (Bagian 5.3), jadi H1 dibaca dari tren (% QoQ, % YoY), bukan dari level lintas operator.

### 3.3 Tujuan teknis (Data Scientist dan ML Engineer)

Membangun sistem berorientasi objek yang mengklasifikasikan sentimen dan topik keluhan, disajikan lewat API dan web interaktif, di-deploy dengan CI/CD, dan dipantau.

### 3.4 Metrik keberhasilan

- Data: minimal 150.000 ulasan nyata dari minimal 3 tahun, dan 12 kuartal data keuangan per operator dengan sumber tercatat.
- Label: gold set 2.000 sampai 3.000 ulasan dengan Cohen's kappa antar-pelabel minimal 0,7 pada sampel ganda 300 ulasan.
- Model sentimen: Macro F1 minimal 0,78 pada test set gold yang dipisah berdasarkan waktu.
- Model topik (multi-label): Macro F1 minimal 0,70 pada test set yang sama, dengan threshold per label.
- API: latensi P95 /predict di bawah 200 ms pada model production, diukur dengan load test pada lingkungan deploy.
- CI/CD: setiap push ke main menjalankan lint, test, build, dan deploy tanpa langkah manual.
- Kualitas kode: cakupan pytest minimal 80 persen, lint dan type check lolos.
- Dokumentasi: README berisi temuan bisnis, rekomendasi, dan keterbatasan.

Metrik analisis tambahan:

- Tabel prediksi (3.2) terkunci di Git sebelum hasil.
- Dekomposisi pendapatan seluler (efek pelanggan, ARPU, bauran) dengan selisih yang dilaporkan.
- Event study mingguan dan replikasi di Indosat serta XL pra-merger.
- Bagian Threats to Validity dan daftar pertanyaan yang tidak dapat dijawab dengan data publik.

## 4. Ruang Lingkup

### 4.1 Dalam lingkup

Scraping ulasan Kelompok A (MyTelkomsel, by.U, myIM3, Bima+), pembersihan teks, penyimpanan data, agregasi SQL, dekomposisi pendapatan seluler, event study dan analisis statistik, pelabelan, pelatihan dan evaluasi model, API inferensi, deteksi lonjakan per versi, dashboard tiga halaman, CI/CD, deployment, dan pemantauan dasar. Kelompok B (myXL, AXISnet) hanya untuk replikasi di jendela pra-merger. Peran XL: pra-merger (2022-Q3 sampai 2025-Q1, 11 kuartal) sebagai uji replikasi dan pembanding tenang; pasca-merger (7 kuartal) hanya deskriptif, karena data keuangan XL, AXIS, dan Smartfren tidak dipisahkan per merek.

### 4.2 Di luar lingkup

Prediksi harga saham, klaim kausalitas, analisis pengguna individual, sistem otentikasi, dan uji asosiasi pada XLSMART pasca-merger. mySmartfren (Kelompok C) ditunda: hanya jendela pasca-merger dan deskriptif, dan ID aplikasinya belum diverifikasi. Fitur berbasis LLM bersifat opsional dan hanya masuk jika dievaluasi.

## 5. Data

### 5.1 Sumber ulasan

- Kelompok A (inti): MyTelkomsel (com.telkomsel.telkomselcm), by.U (com.byu.id), myIM3 (com.pure.indosat.care), Bima+ (com.linkit.bimatri). Setiap ID diverifikasi dengan get\_app sebelum scraping.
- Kelompok B (replikasi): myXL (com.apps.MyXL) dan AXISnet (com.axis.net), hanya hingga 2025-Q1 untuk analisis asosiasi.
- Kelompok C (ditunda): mySmartfren, hanya jendela pasca-merger dan deskriptif.
- Rentang: 2022-07-01 sampai sekarang, sama dengan jendela data keuangan. Tarik dengan urutan NEWEST sampai batas tanggal, lalu lakukan sampling per kuartal sebelum pelabelan dan inferensi.
- Perkiraan ulasan sepanjang masa (Nov 2026): MyTelkomsel sekitar 2,95 juta, myIM3 sekitar 2,82 juta, Bima+ sekitar 644 ribu, myXL sekitar 1,08 juta. Jumlah per kuartal diukur dulu sebelum menarik semuanya.
- MyTelkomsel sejak 2023-Q3 juga melayani IndiHome, sehingga ulasannya bisa memuat keluhan internet rumah. Pedoman label menambah label Lainnya/IndiHome.

Scraper wajib menyimpan: id ulasan, teks, rating, tanggal, versi aplikasi, jumlah thumbs-up, balasan developer, app\_source, dan sort\_mode. Data mentah disimpan permanen dalam Parquet dan tidak diubah. Versi data dilacak dengan DVC atau DagsHub.

### 5.2 Data keuangan

Data keuangan kuartalan tiga operator sudah terkumpul untuk 2022-Q3 sampai 2026-Q3 (17 kuartal tanpa gap): telkomsel\_quarterly.csv, indosat\_quarterly.csv, dan xl\_xlsmart\_quarterly.csv. Kolom: pendapatan total dan seluler, ARPU blended, pelanggan (prabayar dan pascabayar), payload, yield, BTS, flag break, dan sumber dokumen per baris. Standar file: pemisah koma, UTF-8. Data tambahan yang perlu dikumpulkan: events.csv (perubahan paket dan harga, peluncuran, merger, penutupan 3G), Google Trends mingguan, dan indikator makro (indeks keyakinan konsumen, inflasi, penjualan ritel).

### 5.3 Asumsi kesebandingan

- Pelanggan berarti kartu SIM tercatat, bukan orang unik. Angka 8,8 juta dihitung dari puncak 2024-Q2 (159,9 juta) ke 2026-Q3 (151,1 juta).
- Telkomsel: total revenue melompat di 2023-Q3 karena integrasi IndiHome (flag is\_post\_fmc). Untuk tren lintas waktu pakai mobile\_service\_rev.
- Telkomsel 2023-Q4: porsi legacy dan digital berubah tajam dan diduga akibat reklasifikasi, belum diverifikasi ke memo FY23. mobile\_service\_rev stabil sehingga dipakai sebagai ukuran utama.
- XL/XLSMART: merger April 2025 mengubah basis pelanggan (58,8 juta menjadi 82,6 juta). Sebelum merger angka mencakup XL dan AXIS, belum Smartfren. ARPU XL 2022-2023 dibulatkan ke ribuan, dan yield XL dihitung dari mobile\_digital\_rev sehingga tidak sebanding dengan Telkomsel dan Indosat.
- Payload: nilai Telkomsel dalam PB berasal dari TB dibagi 1.024; satuan Indosat perlu dicek dan diseragamkan sebelum membandingkan level yield lintas operator. Analisis lintas operator memakai tren, bukan selisih level.
- Indosat dimulai 2022-Q3, sekitar enam bulan setelah penggabungan IOH, saat integrasi dan penutupan 3G masih berjalan; flag is\_post\_3g\_shutdown dipakai di model.

### 5.4 Kualitas data

Deteksi duplikat, ulasan spam atau bot, ulasan terlalu pendek, dan teks campuran bahasa. Tangani nilai versi aplikasi yang kosong dan laporkan persentasenya. Seluruh keputusan dicatat dalam data dictionary. Tes data otomatis memakai Pandera atau Great Expectations.

## 6. Strategi Pelabelan

Pelabelan adalah risiko terbesar proyek, sehingga dirancang eksplisit.

1. **Gold set.** 2.000 sampai 3.000 ulasan dilabel manual, dipilih secara stratified menurut operator, kuartal, dan rating.
2. **Pedoman label.** Dokumen satu halaman berisi definisi sentimen (positif, netral, negatif) dan empat topik: Harga dan Kuota, Sinyal dan Jaringan, Bug dan Performa Aplikasi, Transaksi dan Pembayaran. Topik bersifat multi-label.
3. **Agreement.** Sampel 300 ulasan dilabel dua kali untuk menghitung Cohen's kappa. Jika di bawah 0,7, pedoman direvisi.
4. **Silver labels.** Sisa data dilabel dengan weak supervision (aturan kata kunci) dan atau model, lalu divalidasi terhadap gold set. Kualitas silver label dilaporkan, tidak diasumsikan.
5. **Pemisahan data.** Test set gold diambil dari periode terbaru dan tidak pernah dipakai untuk pelatihan atau tuning.

## 7. Pemodelan

### 7.1 Model yang dibandingkan

- Baseline: TF-IDF dengan Logistic Regression atau LinearSVC.
- Transformer: fine-tune IndoBERT atau IndoBERTweet pada gold set dan silver set.
- Opsional: zero-shot LLM sebagai pembanding, dengan evaluasi biaya dan latensi.

### 7.2 Protokol evaluasi

- Split berdasarkan waktu (train lama, test baru), bukan acak.
- Laporan per kelas (precision, recall, F1), confusion matrix, dan evaluasi per operator dan per kuartal untuk melihat degradasi.
- Multi-label: threshold dituning per label pada set validasi.
- Kalibrasi: reliability curve agar confidence score bermakna.
- Error analysis: kumpulan contoh salah prediksi yang dikelompokkan berdasarkan penyebab.
- Semua eksperimen dicatat di MLflow (DagsHub): parameter, metrik, artefak, dan versi data.

### 7.3 Pemilihan model production

Model production dipilih berdasarkan trade-off F1, latensi CPU, dan ukuran. Jika model transformer tidak mencapai P95 di bawah 200 ms pada CPU, termasuk setelah quantization atau ONNX, model linear menjadi production dan transformer menjadi pembanding riset. Keputusan dicatat dalam ADR.

### 7.4 Topic discovery tak terawasi

BERTopic dijalankan pada seluruh korpus untuk menemukan topik di luar empat label. Hasil dibandingkan dengan label terawasi dan dilaporkan topik baru yang muncul setelah rilis tertentu.

## 8. Analisis Statistik dan SQL

- Agregasi SQL (DuckDB) menggabungkan ulasan per operator dan per kuartal atau minggu dengan tabel keuangan. Metrik: porsi ulasan negatif per topik, rating rata-rata, keluhan per juta pelanggan (keluhan = ulasan negatif dengan minimal satu topik), serta perubahan pelanggan, ARPU, dan yield.
- Dekomposisi: perubahan pendapatan seluler = efek pelanggan + efek ARPU + bauran. Uji dulu apakah ARPU kali pelanggan mendekati pendapatan seluler; selisihnya dilaporkan sebagai temuan.
- Segmen: penurunan prabayar vs pascabayar, dan payload per pelanggan.
- Waktu: korelasi silang dan lag antara porsi keluhan mingguan dan perubahan pelanggan atau yield; Spearman dengan bootstrap CI.
- Event study mingguan di sekitar event di events.csv (misalnya penyederhanaan starter pack Mar 2025 dan merger XL-Smartfren Apr 2025). Jendela ini dipilih setelah analisis deskriptif, sehingga berstatus eksploratif.
- Regresi panel dengan efek tetap per operator (Telkomsel dan Indosat; XL pra-merger sebagai replikasi) dengan kontrol musim (Lebaran) dan flag break.
- Kontrol negatif dan uji ketahanan: keluhan bug sebagai kontrol; buang satu operator; ganti lag; buang kuartal break.
- Resolusi data: keluhan dan Google Trends mingguan, keuangan kuartalan. Jendela penurunan hanya 7 kuartal, jadi hasil kuartalan dibaca sebagai konteks. Bagian Threats to Validity wajib.

## 9. Deteksi Dini Lonjakan Keluhan

- Unit: versi aplikasi dan jendela hari setelah rilis.
- Aturan: minimal jumlah ulasan per versi, baseline rolling, dan Z-score dengan ambang 2,0 sebagai awal. Bandingkan dengan changepoint detection (CUSUM atau ruptures).
- Backtest: apakah alert historis mendahului penurunan rating. Laporkan precision, recall, dan lead time.
- Versi tanpa data versi yang cukup dilaporkan terpisah.

## 10. Persyaratan Fungsional

### Data pipeline (src/)

- FR-1 PlayStoreScraper: menarik ulasan per ID aplikasi dengan jeda dan retry, menyimpan Parquet, dan dapat dilanjutkan (resume).
- FR-2 TextCleaner: membersihkan tanda baca, huruf kecil, normalisasi slang dengan kamus, dan memetakan tanggal ke kuartal (YYYY-QX).
- FR-3 SQL: kueri DuckDB menggabungkan agregasi ulasan dengan metrik keuangan.
- FR-4 QualityChecker: menjalankan tes data dan menghasilkan laporan kualitas.

### Machine learning

- FR-5 Klasifikasi sentimen tiga kelas.
- FR-6 Klasifikasi multi-topik empat label.
- FR-7 Trainer dan Predictor berbasis kelas dengan antarmuka yang sama untuk baseline dan transformer.

### API (api/)

- FR-8 POST /api/v1/predict: input JSON dengan teks, output sentimen, daftar topik, confidence, versi model, dan waktu proses. Validasi panjang input dan batas laju.
- FR-9 GET /api/v1/analytics/business: data historis sentimen dan ARPU per kuartal dan operator, termasuk interval kepercayaan.
- FR-10 GET /api/v1/analytics/early-warning: daftar versi dengan status Normal atau Spike Alert.
- FR-11 GET /health, /ready, dan /metrics (format Prometheus).

### Frontend (static/)

- FR-12 Halaman 1, Executive Dashboard: KPI cards (total ulasan, persen keluhan harga, tren ARPU) dan grafik dua sumbu Telkomsel vs Indosat.
- FR-13 Halaman 2, Early Warning: tabel dan grafik tren keluhan per versi dengan indikator status.
- FR-14 Halaman 3, Live NLP Simulator: formulir untuk menguji kalimat dan melihat hasil JSON yang divisualisasikan.

### MLOps

- FR-15 CI: pada setiap push, jalankan ruff, mypy, pytest dan build Docker.
- FR-16 CD: pada push ke main, kirim image ke registry dan deploy otomatis.
- FR-17 Pemantauan: request rate, latensi P95, error rate, dan distribusi prediksi, ditambah drift teks (PSI atau Evidently) pada skrip terjadwal.

## 11. Persyaratan Non-Fungsional

- Performa: P95 /predict di bawah 200 ms, diukur dengan Locust atau k6.
- Keandalan: health check, penanganan error terstruktur, dan logging JSON.
- Keamanan: tanpa secret di repo, validasi input, rate limiting, dan pemindaian image (Trivy).
- Reproducibility: pyproject.toml, lockfile, seed tetap, config YAML, dan Makefile.
- Privasi: nama pengguna dihapus dari data yang dipublikasikan.

## 12. Arsitektur dan Tech Stack

- Bahasa dan paket: Python 3.10 atau lebih baru, OOP, pyproject.toml.
- Data: google-play-scraper, pandas, Parquet, DuckDB, Sastrawi, DVC atau DagsHub.
- ML: scikit-learn, Hugging Face Transformers, MLflow di DagsHub, ONNX opsional.
- Analisis: statsmodels, scipy, BERTopic, ruptures.
- Backend: FastAPI, Pydantic, Uvicorn.
- Frontend: HTML5, Tailwind CSS (CDN), JavaScript vanilla, Chart.js.
- DevOps: Docker, GitHub Actions, Prometheus, Grafana.
- Kualitas: ruff, mypy, pre-commit, pytest.

Keputusan arsitektur dicatat sebagai ADR pendek, misalnya pemilihan model production, DuckDB dibanding PostgreSQL, dan platform deploy.

## 13. Strategi Komputasi Hybrid (tanpa GPU lokal)

- Repo Git adalah sumber kebenaran. Semua logika berada di paket Python modular, bukan di notebook.
- Pengembangan, tes, dan iterasi memakai VS Code di CPU lokal dengan subset 500 baris.
- Pelatihan transformer dan inferensi massal berjalan di Kaggle (utama) atau Colab (cadangan) dengan GPU. Notebook tipis: clone repo, pip install -e ., lalu jalankan skrip dengan config YAML.
- Tracking jarak jauh: MLFLOW\_TRACKING\_URI mengarah ke DagsHub. Model dan artefak disimpan di registry atau Hugging Face Hub, bukan di disk sesi.
- Secret disimpan di Kaggle Secrets atau Colab Secrets.
- Hemat komputasi: fp16, max\_length 128, checkpoint per epoch dengan resume, dan simpan hasil inferensi massal ke Parquet agar analisis lanjutan berjalan di CPU.
- Production tidak memerlukan GPU.

## 14. Deployment dan Observability

### 14.1 Keputusan platform: Hugging Face Spaces sebagai utama

Hugging Face Spaces (Docker SDK) dipilih sebagai tempat deploy utama karena gratis untuk CPU dasar, mendukung Docker langsung, dan menyatu dengan ekosistem model. Railway menjadi opsi cadangan karena berbasis kredit berbayar. Alasan dan trade-off dicatat dalam ADR. Verifikasi batas gratis, perilaku tidur otomatis, dan kebijakan terkini kedua platform pada awal proyek.

Konsekuensi: Space gratis dapat tertidur saat tidak aktif, sehingga README menyertakan GIF atau video demo dan tautan ke repo. Aplikasi harus mendengarkan pada port yang diminta Space.

### 14.2 CI/CD

GitHub Actions: lint, type check, pytest, build Docker, scan Trivy, lalu push ke Hugging Face Space (atau registry) pada branch main. Staging dapat berupa Space terpisah.

### 14.3 Pemantauan

Endpoint /metrics dibaca Prometheus. Karena layanan gratis sulit di-scrape dari Grafana Cloud, demonstrasi pemantauan penuh dijalankan lewat docker-compose (API, Prometheus, Grafana) yang disertakan di repo, dengan tangkapan layar dan satu dashboard Grafana (request rate, P95, error rate, distribusi prediksi) di README.

## 15. Struktur Direktori

- src/: scraper.py, cleaner.py, quality.py, trainer.py, predictor.py, analysis/
- api/: main.py, schemas.py, metrics.py
- static/: tiga halaman, js/, css/
- sql/: kueri agregasi dan join
- configs/: YAML per eksperimen
- scripts/: train.py, batch\_infer.py
- notebooks/: kaggle\_train.ipynb (tipis), eda.ipynb
- tests/: tes unit, data, dan kontrak API
- docs/: PRD, ADR, data dictionary, pedoman label, model card
- monitoring/: docker-compose, prometheus.yml, dashboard Grafana
- .github/workflows/: ci.yml dan cd.yml
- Dockerfile, pyproject.toml, Makefile, README.md

## 16. Rencana Eksekusi 4 Minggu

### Minggu 1: Data dan fondasi

Selesai: repo, CI hijau, verifikasi ID aplikasi, dan data keuangan tiga operator (17 kuartal). Berikutnya: kunci judul, pertanyaan riset, dan tabel prediksi (3.2) di Git; kumpulkan events.csv, Google Trends, dan indikator makro; config dan scraper Kelompok A dengan sampling per kuartal; EDA dan kualitas data; skema DuckDB; pedoman label dan mulai melabel gold set.

### Minggu 2: Analisis bisnis

Selesaikan gold set dan kappa, silver label, dan agregasi mingguan. Jalankan dekomposisi pendapatan seluler, analisis segmen, korelasi silang dan lag, event study, regresi panel, uji ketahanan, serta Threats to Validity. Draf temuan dan executive summary siap dibaca di akhir minggu.

### Minggu 3: Model dan sistem

Eksperimen model di MLflow, error analysis, pilih model production, FastAPI dengan tes, Docker, deteksi dini dengan backtest, dan BERTopic.

### Minggu 4: Produk dan penutup

Frontend tiga halaman, CI/CD penuh, deploy ke Hugging Face Spaces, pemantauan lewat docker-compose, load test, model card, ADR, README dengan rekomendasi bisnis, dan studi kasus LinkedIn. Sisakan tiga hari cadangan.

### Urutan prioritas bila waktu mepet

1. Label dan evaluasi yang kredibel. 2. Analisis statistik dengan keterbatasan yang jujur. 3. API, Docker, CI/CD. 4. README dan rekomendasi. 5. Bonus: BERTopic, drift, LLM.

## 17. Risiko dan Mitigasi

- Scraping dibatasi laju: jeda, retry, resume, dan simpan bertahap.
- Versi aplikasi sering kosong: ukur persentase di hari 1 dan sesuaikan analisis early warning.
- Data keuangan tidak sebanding antar operator: Comparability Assumptions dan variabel penanda break.
- Sampel kuartal kecil: interval kepercayaan, uji nonparametrik, dan klaim terbatas.
- Kappa rendah: revisi pedoman label dan tambah sampel ganda.
- Transformer terlalu lambat di CPU: model linear sebagai production.
- Kuota GPU habis: tes lokal dulu, checkpoint, dan Colab sebagai cadangan.
- Space gratis tertidur: demo rekaman di README.

Risiko tambahan setelah pertanyaan riset diperbarui:

- Jendela penurunan hanya 7 kuartal (2025-Q1 sampai 2026-Q3): pakai sinyal mingguan dan Google Trends, baca hasil kuartalan sebagai konteks.
- Rentang waktu 2025 dipilih setelah melihat data: tandai eksploratif dan replikasi di Indosat.
- Satuan payload dan definisi yield tidak seragam antar operator: seragamkan sebelum membandingkan level, atau pakai tren.
- Churn kotor tidak tersedia publik: kesimpulan dibatasi pada konsisten atau tidak konsisten dengan.
- Merger XL-Smartfren: XL pasca-merger hanya deskriptif.

## 18. Etika dan Legal

Ulasan bersifat publik. Data pribadi tidak disimpan atau dipublikasikan, dan nama pengguna dihapus. Patuhi batas laju scraping dan syarat layanan. Proyek bersifat riset independen dan tidak mewakili operator mana pun.

## 19. Deliverables

- Repo GitHub dengan kode modular, tes, dan CI/CD hijau.
- Dataset terversi, data dictionary, dan pedoman label.
- Model card dan eksperimen MLflow publik.
- Layanan hidup di Hugging Face Spaces dan demo rekaman.
- Dashboard Grafana (tangkapan layar) dan hasil load test.
- README dengan narasi, temuan, rekomendasi bisnis, dan keterbatasan.
- Studi kasus LinkedIn.

## 20. Prioritas Kedalaman (Tier)

Semua item PRD tetap dikerjakan. Tier menentukan urutan dan kedalaman, bukan apa yang dibuang.

- Tier 1 (inti analyst, dikerjakan paling dalam): pertanyaan bisnis dan KPI tree, SQL serius (join, window function, CTE), analisis statistik dengan batas kesimpulan, audit kualitas dan cakupan data, segmentasi, insight dan rekomendasi bisnis, gold set dan evaluasi model yang jujur.
- Tier 2 (harus berfungsi dan teruji): baseline TF-IDF, API FastAPI, Docker, CI/CD, deploy, dashboard tiga halaman.
- Tier 3 (pendalaman): IndoBERT, BERTopic, drift teks, dashboard Grafana lengkap, fitur LLM yang dievaluasi.

Aturan: Tier 3 dimulai setelah Tier 1 dan Tier 2 punya versi utuh. Jika waktu kurang, durasi proyek diperpanjang, bukan kualitas Tier 1 diturunkan.

## 21. Penguat untuk Posisi Data Analyst

- KPI tree dan data dictionary bisnis: definisi tertulis untuk keluhan per juta pelanggan, negative share, complaint rate per topik, dan ambang naik atau turun yang bermakna.
- SQL portofolio: kumpulan file .sql rapi di sql/ dengan komentar tujuan bisnis, memakai CTE, window function (LAG, rolling average), dan agregasi kuartalan.
- Segmentasi: analisis dipecah per topik, per versi aplikasi, per rentang rating, dan per operator. Setiap pemecahan mencatat apa yang berubah dibanding angka agregat.
- Dashboard BI tambahan: satu dashboard Looker Studio atau Power BI dari data akhir, selain dashboard HTML kustom.
- Executive summary satu halaman: temuan utama, angka kunci, rekomendasi, keterbatasan.
- Rekomendasi yang dapat ditindaklanjuti: minimal tiga, masing-masing dengan bukti, dampak yang diperkirakan, dan keterbatasannya.
- Narasi README sebagai cerita data: masalah, pendekatan, temuan, dampak, keterbatasan.

## 22. Checkpoint dan Aturan Keterlambatan

Setiap minggu punya gerbang (gate). Gerbang lolos hanya jika semua kriterianya terpenuhi, bukan jika waktunya habis.

- Gerbang minggu 1: data mentah dua operator tersimpan dengan bukti cakupan per kuartal, minimal 8 kuartal keuangan bersumber per operator, repo dengan CI hijau, pedoman label siap, pelabelan gold set dimulai.
- Gerbang minggu 2: gold set selesai dengan kappa terukur, analisis statistik dan SQL selesai, draf executive summary dan Threats to Validity tertulis.
- Gerbang minggu 3: model baseline dievaluasi, model production terpilih, API dan tes berjalan, deteksi dini dengan backtest.
- Gerbang minggu 4: dashboard, deploy, pemantauan, README, dan studi kasus selesai.

Aturan keterlambatan: keterlambatan di bawah dua hari diserap oleh hari cadangan. Keterlambatan dua hari atau lebih menggeser seluruh jadwal setelahnya sebesar keterlambatan itu. Jadwal ditinjau di akhir setiap minggu berdasarkan kenyataan, dan kualitas Tier 1 tidak diturunkan untuk mengejar tanggal.
