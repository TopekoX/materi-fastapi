# Proyek Praktik Tahap 6

## Tujuan pembelajaran

Setelah mengerjakan halaman ini, kamu mampu:

- [ ] Menyiapkan aplikasi yang sudah teruji (Tahap 5) agar siap dijalankan di produksi.
- [ ] Menambahkan pembeda lingkungan dan aturan produksi pada konfigurasi.
- [ ] Menambahkan logging terstruktur dengan request ID ke aplikasi nyata.
- [ ] Membuat endpoint *liveness* (`/kesehatan`) dan *readiness* (`/siap`), dan membedakan keduanya.
- [ ] Menutup dokumentasi interaktif di produksi.
- [ ] Mengemas aplikasi dengan `Dockerfile` dan Compose, membangunnya, dan menjalankannya sebagai container.
- [ ] Menilai kesiapan rilis dengan `periksa_rilis.py`.

## Prasyarat

- Sudah mengerjakan [Proyek Praktik Tahap 5](../09-pengujian/proyek-tahap-5.md). Tahap 6 memakai kode dan seluruh pengujiannya.
- Sudah membaca halaman Modul 10 sebelumnya: [Server Produksi](server-produksi.md), [Container](container.md), [Variabel Environment](variabel-environment.md), [Logging](logging.md), dan [Checklist Rilis](checklist-rilis.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **SQLModel 0.0.48**, **Alembic 1.20.1**, **pydantic-settings 2.16.1**, **pytest 9.1.1**, dan **pytest-cov 7.1.0** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

!!! success "Docker sudah dijalankan"
    `docker build`, `docker run`, dan `docker compose up` untuk tahap ini dijalankan di Ubuntu dengan Docker Engine 29.9.2 dan Compose 5.6.1. Hasilnya ada di halaman [Container](container.md#yang-sudah-diuji). Pengujian di Windows dan macOS (Docker Desktop) belum dilakukan. Bagian "Menjalankan seperti di container" di bawah adalah percobaan awal di Windows tanpa Docker, dan dipertahankan sebagai catatan.

## Tentang tahap ini

Tahap 6 melanjutkan **TugasKu API** dari Tahap 5. Rangkaian 54 pengujian dari Tahap 5 tetap ada dan tetap lulus. Yang ditambahkan:

| Perubahan | Berkas | Dari halaman |
|---|---|---|
| `lingkungan`, aturan produksi, pengaturan log | `app/config.py` | [Variabel Environment](variabel-environment.md) |
| Logging dan request ID | `app/pengaturan_log.py`, `app/main.py` | [Logging](logging.md) |
| `/kesehatan`, `/siap`, docs ditutup di produksi | `app/main.py` | [Variabel Environment](variabel-environment.md), [Checklist Rilis](checklist-rilis.md) |
| Pengemasan | `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `requirements.txt`, `.env.contoh` | [Container](container.md) |
| Pengujian baru (13 buah) | `tests/test_deploy.py` | [Pengujian](../09-pengujian/proyek-tahap-5.md) |

Berkas `app/database.py`, `app/errors.py`, `app/keamanan.py`, `app/models.py`, `app/routers/`, `alembic/`, dan `tests/` lainnya **sama dengan Tahap 5**.

### Struktur

```text
proyek/tahap-6/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.contoh
├── requirements.txt          (dependensi produksi, versi dikunci)
├── alembic.ini
├── alembic/
├── pytest.ini
├── app/
│   ├── config.py             (diubah)
│   ├── pengaturan_log.py     (baru)
│   ├── main.py               (diubah)
│   └── ...                   (sama dengan Tahap 5)
└── tests/
    ├── test_deploy.py        (baru)
    └── ...                   (sama dengan Tahap 5)
```

## Langkah menjalankan

Dari folder `examples/fastapi/proyek/tahap-6`, di dalam lingkungan virtual yang sudah memasang `examples/fastapi/requirements.txt`:

```powershell
$env:TUGASKU_SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
alembic upgrade head
fastapi dev app/main.py
```

Pengujian:

```powershell
python -m pytest -q
```

## Kode lengkap

### `app/config.py`

```python title="app/config.py"
--8<-- "fastapi/proyek/tahap-6/app/config.py"
```

### `app/main.py`

```python title="app/main.py"
--8<-- "fastapi/proyek/tahap-6/app/main.py"
```

### `app/pengaturan_log.py`

Isinya sama dengan `pengaturan_log.py` di halaman [Logging](logging.md), dipindahkan ke dalam paket `app`. Lihat halaman itu untuk penjelasan setiap kelasnya.

### `tests/test_deploy.py`

```python title="tests/test_deploy.py"
--8<-- "fastapi/proyek/tahap-6/tests/test_deploy.py"
```

### `Dockerfile`

```dockerfile title="Dockerfile"
--8<-- "fastapi/proyek/tahap-6/Dockerfile"
```

### `docker-compose.yml`

```yaml title="docker-compose.yml"
--8<-- "fastapi/proyek/tahap-6/docker-compose.yml"
```

### `.env.contoh`

```text title=".env.contoh"
--8<-- "fastapi/proyek/tahap-6/.env.contoh"
```

## Penjelasan kode

### `config.py`

- `lingkungan` dibatasi `Literal` pada tiga nilai; nilai lain ditolak saat aplikasi mulai.
- `log_level` dan `log_format` juga `Literal`, sehingga `TUGASKU_LOG_LEVEL=CERewET` ditolak (teruji).
- `extra="ignore"` membuat entri lain di `.env` (misalnya milik Compose) tidak menggagalkan aplikasi. Risikonya: salah ketik nama variabel tidak ketahuan. Lihat [Variabel Environment](variabel-environment.md).
- `periksa_aturan_produksi` hanya berlaku bila `lingkungan == "produksi"`. Ia menolak origin `*` dan kunci yang masih berawalan `KUNCI_CONTOH`. Aturan mode debug dari halaman Variabel Environment tidak dipakai di sini karena aplikasi ini tidak punya pengaturan debug.

### `main.py`

- `atur_logging(...)` dipanggil sekali saat modul diimpor, dengan level dan format dari konfigurasi.
- Dokumentasi (`docs_url`, `redoc_url`, `openapi_url`) bernilai `None` di produksi sehingga `/docs`, `/redoc`, dan `/openapi.json` menjawab `404`. Menutup dokumentasi adalah **keputusan**, bukan keharusan; pilihlah sesuai kebutuhan timmu.
- Middleware `catat_request` sama dengan di halaman Logging: menentukan request ID, mencatat satu baris per request, dan menaruh ID di header `X-Request-ID`.
- `/kesehatan` menjawab selama proses hidup dan tidak menyentuh basis data. Ini *liveness*: "prosesnya hidup?".
- `/siap` menjalankan `SELECT 1` lewat sesi basis data. Bila gagal, ia mencatat galat dan menjawab `503`. Ini *readiness*: "siap melayani pekerjaan?". Pembeda keduanya penting: bila basis data mati, memulai ulang proses tidak menolong, jadi `/kesehatan` tetap `200` tetapi `/siap` menjadi `503`.
- Kedua endpoint ini tidak memerlukan login, supaya bisa dipanggil proksi atau orkestrator.

### `Dockerfile`, Compose, dan `.env.contoh`

Sama dengan yang dijelaskan di halaman [Container](container.md): berkas dependensi disalin lebih dulu agar lapisan `pip install` bisa dipakai ulang, aplikasi berjalan sebagai pengguna `aplikasi` (bukan root), basis data SQLite ada di `/data` yang dipasang sebagai volume, dan rahasia datang dari environment saat container dijalankan. `.env.contoh` hanya berisi nilai tiruan; salin menjadi `.env` untuk dipakai Compose.

## Mencoba

### Pengujian

Hasil nyata:

```text
67 passed in 5.20s
```

Rinciannya: 54 pengujian dari Tahap 5 ditambah 13 pengujian dari `test_deploy.py`. Cakupan cabang untuk paket `app` bernilai 98% (359 pernyataan, 6 belum tercakup): 4 di `pengaturan_log.py` (kelas `FormatJson`, yang diuji di halaman [Logging](logging.md), bukan di sini) dan 2 di `database.py` (fungsi `get_session` asli, yang selalu diganti saat pengujian).

### Merusak aplikasi dengan sengaja

Seperti di Tahap 5, mutu pengujian diuji dengan merusak aplikasi:

| Kerusakan | Hasil |
|---|---|
| Aturan produksi dimatikan (`if False:`) | 2 pengujian gagal |
| Dokumentasi selalu terbuka di produksi | 1 pengujian gagal |
| `/siap` tidak lagi menyentuh basis data | 1 pengujian gagal |

Kerusakan ketiga **awalnya lolos tanpa terdeteksi**: pengujian `/siap` hanya memeriksa kasus basis data sehat, sehingga tidak bisa membedakan `/siap` yang benar dari yang pura-pura. Itu dibenahi dengan menambah `test_siap_gagal_503_bila_basis_data_bermasalah` (sesi yang sengaja rusak), sekaligus mengubah `/siap` agar menjawab `503` dan tidak `500`. Setelah itu kerusakan ketiga tertangkap.

### Menjalankan seperti di container

Sebelum Docker dicoba, langkah di `Dockerfile` diemulasikan tanpa Docker di Windows: salin `app`, `alembic`, dan `alembic.ini` ke folder `code`; siapkan folder `data` kosong; jalankan migrasi dari folder `data` dengan `PYTHONPATH` menunjuk ke `code`; jalankan server dari `code` dengan variabel environment produksi (`lingkungan=produksi`, log JSON, origin `https://tugasku.contoh`, kunci acak 64 karakter).

Migrasi membuat `database.db` di folder `data`. Lalu:

| Permintaan | Hasil |
|---|---|
| `GET /kesehatan` | `200` |
| `GET /siap` | `200`, `{"status":"siap"}` |
| `GET /docs`, `GET /openapi.json` | `404` |
| `POST /daftar` (pengguna `budi`) | `201` |
| Server dimulai ulang, `POST /daftar` lagi | `409 NAMA_PENGGUNA_SUDAH_ADA` (data bertahan) |

Log di terminal server berformat JSON, misalnya:

```text
{"waktu": "2026-10-26T14:00:49.973+00:00", "level": "INFO", "logger": "tugasku.aplikasi", "request_id": "79a95028", "pesan": "GET /siap -> 200 (2.6 ms)"}
{"waktu": "2026-10-26T14:00:50.049+00:00", "level": "INFO", "logger": "tugasku.aplikasi", "request_id": "69c77717", "pesan": "POST /daftar -> 201 (57.0 ms)"}
```

Dengan `TUGASKU_ORIGIN_DIIZINKAN='["*"]'` di produksi, server **menolak mulai**:

```text
ValidationError: 1 validation error for Settings
  Value error, Konfigurasi produksi tidak aman: origin_diizinkan tidak boleh berisi '*'
```

### Temuan nyata: `/siap` menangkap basis data yang tidak terjangkau

Pada percobaan pertama, `DATABASE_URL` yang saya berikan memakai jalur gaya Git Bash (`/c/Users/...`) yang tidak dikenal SQLite di Windows. Hasilnya:

| Permintaan | Hasil |
|---|---|
| `GET /kesehatan` | `200` |
| `GET /siap` | `503` |
| `POST /daftar` | `500` (`sqlite3.OperationalError: unable to open database file`) |

Ini kebetulan memperlihatkan fungsi dua endpoint itu: proses hidup (`/kesehatan` `200`), tetapi tidak siap melayani (`/siap` `503`). Perbaikannya hanya menulis jalur Windows (`C:/Users/...`). Itu adalah kesalahan dalam percobaan, bukan dalam kode aplikasi.

### Penilaian kesiapan

```powershell
python ..\..\10-deployment\checklist-rilis\periksa_rilis.py .
```

Hasil nyata untuk `tahap-6`:

```text
[LULUS] .env dan *.db diabaikan Git - .gitignore
[LULUS] .dockerignore menutup .env - .dockerignore ada
[LULUS] container berjalan sebagai non-root - USER aplikasi
[LULUS] tidak ada rahasia di Dockerfile/Compose - bersih
[LULUS] versi dependensi dikunci (==) - 6 paket
[LULUS] CORS tidak memakai '*' di kode - tidak ditemukan
[LULUS] tidak ada rahasia tertulis di kode - tidak ditemukan
[LULUS] ada pengujian - berkas test_*.py ditemukan
[LULUS] ada konfigurasi migrasi (Alembic) - alembic.ini ada

0 gagal dari 9 pemeriksaan
```

Bandingkan dengan Tahap 5 yang `1 gagal dari 9`. Ingat bahwa pemeriksa ini heuristik: `LULUS` bukan jaminan aman.

## Yang belum terverifikasi

| Hal | Status |
|---|---|
| `docker build`, `docker run`, `docker compose up` | Dijalankan di Ubuntu (lihat [Container](container.md#yang-sudah-diuji)) |
| Ukuran image | 1,8 GB menurut `docker images`; varian `slim` tidak dicoba. Pengguna `aplikasi` (uid 1000) terbukti terbentuk dan memiliki `/data` |
| Volume | Data bertahan setelah container dibuat ulang (diuji). `restart: unless-stopped` tidak diuji |
| HTTPS, proksi balik (reverse proxy), dan header `X-Forwarded-*` | Diuji dengan Nginx dan sertifikat self-signed di [Reverse Proxy dan HTTPS](reverse-proxy-https.md) |
| Linux | Hanya Ubuntu dengan Docker Engine; seluruh pengujian aplikasi (`pytest`) dan penilaian kesiapan tetap dijalankan di Windows |
| macOS dan Docker Desktop | Tidak diuji |
| Health check Docker yang memanggil `/kesehatan` | Diuji lewat Compose di [Reverse Proxy dan HTTPS](reverse-proxy-https.md). Probe Kubernetes dan instruksi `HEALTHCHECK` di `Dockerfile` tidak diuji |
| Pemindai kerentanan image | Tidak dibahas |
| Basis data selain SQLite untuk produksi | Tidak diuji |
| Beberapa worker dengan SQLite | Tidak diuji pada aplikasi ini; lihat peringatan tentang status di memori pada [Server Produksi](server-produksi.md) |

## Kesalahan umum

| Kesalahan | Penjelasan |
|---|---|
| Memakai `/kesehatan` sebagai readiness | Ia tetap `200` saat basis data mati. Pakai `/siap` untuk kesiapan. |
| Menaruh `SELECT 1` pada liveness | Gangguan basis data membuat orkestrator memulai ulang proses terus-menerus, padahal tidak menolong. |
| Lupa `alembic upgrade head` sebelum server mulai | Tabel tidak ada; `/siap` tetap bisa `200` karena hanya menjalankan `SELECT 1`. Migrasi tetap harus dijalankan. |
| Menulis jalur SQLite gaya Linux di Windows | Contoh nyata di atas: `unable to open database file`. |
| Mengisi `TUGASKU_SECRET_KEY` dengan kunci contoh di produksi | Ditolak saat mulai oleh `periksa_aturan_produksi`. |
| Menaruh `.env` di image | Tutup dengan `.dockerignore`; suntikkan lewat environment. |
| Menganggap pengujian lulus berarti image berhasil dibangun | Pengujian tidak menjalankan Docker. |

## Latihan

1. **Dasar.** Apa beda `/kesehatan` dan `/siap`? Mana yang berubah menjadi `503` saat basis data tidak terjangkau?
2. **Prediksi.** Aplikasi dijalankan dengan `TUGASKU_LINGKUNGAN=produksi` dan `TUGASKU_SECRET_KEY=ganti-dengan-kunci-acak-minimal-32-karakter`. Apa yang terjadi?
3. **Praktik.** Tambahkan aturan produksi: `database_url` tidak boleh mengandung `sqlite`. Tulis pengujian untuk aturan itu di `test_deploy.py`, lalu pastikan pengujian lama masih lulus.
4. **Analisis.** Mengapa `/siap` tidak boleh meminta login?

??? success "Kunci jawaban"
    1. `/kesehatan` menandakan proses hidup dan tidak menyentuh basis data; `/siap` memeriksa basis data. Yang menjadi `503` adalah `/siap`.
    2. Aplikasi menolak mulai: kunci itu berawalan `KUNCI_CONTOH`, sehingga `periksa_aturan_produksi` melempar `ValidationError` "secret_key masih kunci contoh" (teruji pada `test_produksi_menolak_konfigurasi_berbahaya`).
    3. Tambahkan `if "sqlite" in self.database_url: masalah.append("database_url tidak boleh SQLite di produksi")` di blok produksi. **Perhatian:** nilai bawaan `database_url` memakai SQLite, jadi pengujian produksi yang sudah ada perlu memberikan `database_url` non-SQLite, dan emulasi container di halaman ini (yang memakai SQLite) tidak akan lagi bisa mulai dalam mode produksi. Ini penerapan pola dan tidak dijalankan di halaman ini.
    4. Proksi dan orkestrator memanggilnya tanpa kredensial; bila butuh login, mereka akan selalu menerima `401` dan menganggap aplikasi tidak siap.

## Ringkasan

- Tahap 6 mengubah aplikasi yang teruji menjadi aplikasi yang siap dijalankan: konfigurasi per lingkungan, logging berrequest-ID, endpoint kesehatan, dan pengemasan.
- Aturan produksi di `Settings` membuat konfigurasi berbahaya menggagalkan aplikasi saat mulai.
- `/kesehatan` (hidup) dan `/siap` (siap) berbeda; hanya `/siap` yang menyentuh basis data.
- 67 pengujian lulus (54 lama + 13 baru); tiga kerusakan sengaja tertangkap setelah satu pengujian ditambah.
- Image terbangun dan berjalan di Docker (Ubuntu): migrasi, `/kesehatan`, `/siap`, pendaftaran, pengguna non-root, data yang bertahan di volume, dan penghentian baik-baik terbukti. Isi image dan Docker Desktop belum diperiksa.
- `periksa_rilis.py` melaporkan 0 gagal dari 9 pemeriksaan; ia heuristik, bukan jaminan.

## Langkah berikutnya

Kembali ke [Modul 10: Deployment](index.md). Dengan ini kurikulum utama selesai; lihat [Peta Belajar](../../peta-belajar.md) untuk ringkasan seluruh modul.
