# Container

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan apa itu container dan image, dan masalah yang dipecahkannya.
- [ ] Membaca dan menjelaskan setiap baris `Dockerfile` untuk aplikasi FastAPI.
- [ ] Menjelaskan mengapa `requirements.txt` disalin lebih dulu, mengapa bentuk *exec* dipakai pada `CMD`, dan mengapa satu proses per container.
- [ ] Menyimpan data SQLite di volume agar tidak hilang saat container diganti.
- [ ] Menyuntikkan rahasia ke container tanpa menanamkannya di image.
- [ ] Menjalankan migrasi Alembic untuk basis data di volume.
- [ ] Mengetahui secara jujur bagian mana yang sudah diuji dan mana yang belum.

## Prasyarat

- Sudah membaca [Server Produksi](server-produksi.md) dan [Konfigurasi dan Environment](../08-struktur-proyek/konfigurasi-environment.md).
- Sudah mengerjakan [Proyek Praktik Tahap 5](../09-pengujian/proyek-tahap-5.md). Dockerfile di halaman ini mengemas aplikasi Tahap 6, yaitu Tahap 5 ditambah konfigurasi dan logging dari Modul 10 (kodenya ada di [Proyek Praktik Tahap 6](proyek-tahap-6.md)).
- Docker Engine dan plugin Docker Compose terpasang.

!!! info "Versi yang diuji"
    Perintah Docker di halaman ini dijalankan dengan **Docker Engine 29.9.2** dan **Docker Compose 5.6.1** di **Ubuntu Linux**. Image dasar `python:3.14` berisi **Python 3.14.9**. Dependensi aplikasi dikunci di `requirements.txt` (FastAPI 0.162.0, FastAPI CLI 0.0.32, Uvicorn 0.54.0, SQLModel 0.0.48, Alembic 1.20.1). Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini).

!!! success "Dibangun dan dijalankan dengan Docker"
    `docker build`, `docker run`, dan `docker compose up` benar-benar dijalankan untuk halaman ini. Hasilnya ada di bagian [Yang sudah diuji](#yang-sudah-diuji). Bagian yang tidak diuji dicatat di [Yang belum diuji](#yang-belum-diuji). Pengujian hanya di Linux; Docker Desktop di Windows atau macOS belum dicoba.

## Konsep

### Masalah: "di komputerku jalan"

Aplikasi bergantung pada versi Python, pustaka, dan pengaturan sistem. Di komputer lain atau server, sedikit perbedaan bisa membuatnya gagal. **Container** menyelesaikannya dengan mengemas aplikasi **beserta lingkungannya** (Python, pustaka, berkas) menjadi satu paket yang berjalan sama di mana pun Docker tersedia.

| Istilah | Arti |
|---|---|
| **Image** | Paket yang berisi aplikasi dan lingkungannya; dibuat dari `Dockerfile`. Tidak berubah setelah dibuat. |
| **Container** | Image yang sedang berjalan. Dari satu image bisa dijalankan banyak container. |
| **Dockerfile** | Berkas resep: langkah-langkah membangun image. |
| **Volume** | Penyimpanan di luar container yang bertahan walau container dihapus. |
| **Daemon** | Proses Docker di latar belakang yang melakukan pekerjaan sebenarnya. |

### Prinsip untuk FastAPI

Dokumentasi FastAPI menganjurkan:

- Membangun image dari image resmi Python.
- Menyalin `requirements.txt` **lebih dulu**, agar Docker memakai ulang lapisan pemasangan dependensi selama dependensi tidak berubah.
- Memakai bentuk **exec** untuk `CMD` (dengan tanda kurung siku), agar FastAPI bisa berhenti baik-baik dan peristiwa `lifespan` berjalan. Bentuk *shell* disebutnya perlu dihindari.
- Menjalankan **satu proses per container** bila memakai sistem pengelola cluster (Kubernetes, Docker Swarm, Nomad), dan menyerahkan replikasi ke sistem itu. `--workers` hanya untuk kasus khusus seperti satu server dengan Docker Compose.
- Menambahkan `--proxy-headers` bila ada proksi (misalnya Nginx atau Traefik) yang menangani HTTPS di depan container. (Teks `--help` menunjukkan opsi ini aktif secara bawaan.)

## Kode lengkap

Berkas ada di `examples/fastapi/proyek/tahap-6/`, di akar proyek yang sama dengan `app/`, `alembic/`, dan `alembic.ini`. Satu kumpulan berkas ini dipakai oleh halaman ini dan [Proyek Praktik Tahap 6](proyek-tahap-6.md).

### `Dockerfile`

```dockerfile title="Dockerfile"
--8<-- "fastapi/proyek/tahap-6/Dockerfile"
```

### `requirements.txt`

```text title="requirements.txt"
--8<-- "fastapi/proyek/tahap-6/requirements.txt"
```

Hanya dependensi untuk menjalankan aplikasi. `pytest` dan `pytest-cov` tidak dimasukkan, karena image produksi tidak perlu menjalankan pengujian.

### `.dockerignore`

```text title=".dockerignore"
--8<-- "fastapi/proyek/tahap-6/.dockerignore"
```

### `docker-compose.yml`

```yaml title="docker-compose.yml"
--8<-- "fastapi/proyek/tahap-6/docker-compose.yml"
```

## Penjelasan kode

### `Dockerfile`, baris demi baris

| Baris | Fungsi |
|---|---|
| `FROM python:3.14` | Memulai dari image resmi Python. Dokumentasi FastAPI memakai pola yang sama. Versi diselaraskan dengan Python yang diuji di materi ini. |
| `WORKDIR /code` | Folder kerja di dalam image; instruksi berikutnya berjalan dari sini. |
| `COPY ./requirements.txt ...` lalu `RUN pip install ...` | Menyalin daftar dependensi dan memasangnya. Lapisan ini hanya dibangun ulang bila `requirements.txt` berubah. `--no-cache-dir` tidak menyimpan cache unduhan pip (tidak dipakai ulang di image), dan `--upgrade` memperbarui paket yang sudah ada. |
| `COPY ./app`, `./alembic.ini`, `./alembic` | Menyalin kode dan migrasi **setelah** dependensi, karena kode paling sering berubah. Urutan ini menjaga cache lapisan dependensi tetap berlaku. |
| `RUN useradd ... USER aplikasi` | Membuat pengguna biasa dan menjalankan aplikasi dengannya, bukan sebagai `root`. Ini praktik keamanan umum. Folder `/data` dibuat dan dimiliki pengguna itu. |
| `ENV TUGASKU_DATABASE_URL=sqlite:////data/database.db` | Mengarahkan basis data SQLite ke `/data`. Empat garis miring: `sqlite:///` ditambah jalur mutlak `/data/...`. Nama variabelnya mengikuti `env_prefix` di [Konfigurasi dan Environment](../08-struktur-proyek/konfigurasi-environment.md). |
| `VOLUME ["/data"]` | Menandai `/data` sebagai tempat data yang harus bertahan. |
| `ENV PYTHONPATH=/code` | Agar perintah `alembic` yang dijalankan dari folder `/data` tetap bisa mengimpor paket `app`. |
| `EXPOSE 8000` | Dokumentasi bahwa aplikasi memakai port 8000. Tidak membuka port sendiri; pembukaan dilakukan dengan `-p` saat `docker run`. |
| `CMD ["fastapi", "run", "app/main.py", "--port", "8000", "--proxy-headers"]` | Perintah yang berjalan saat container mulai. Bentuk exec, satu proses. |

Perhatikan yang **tidak ada**: `TUGASKU_SECRET_KEY`. Rahasia tidak boleh ditanam di image, karena image bisa dibagikan dan isinya bisa dibaca. Kunci diberikan saat container dijalankan.

### Mengapa menjalankan sebagai bukan-root

Proses di dalam container yang berjalan sebagai `root` memiliki hak besar di dalam container. Bila aplikasi dieksploitasi, penyerang mendapat hak itu. Pengguna biasa membatasi dampaknya. (Ini praktik umum; efeknya tidak diuji di sini.)

### Mengapa `.dockerignore`

Docker mengirim seluruh folder proyek ke daftar bahan build. `.dockerignore` mengecualikan yang tidak diperlukan, dan terutama yang berbahaya: `*.db` (data), `.env` (rahasia), `.git/`, `.venv/`, dan `tests/`. Tanpa itu, berkas rahasia atau data bisa ikut masuk ke image. (Pengecualian `!.env.contoh` mempertahankan berkas contoh.)

### Docker Compose

Compose menjelaskan cara menjalankan container dalam satu berkas:

- `build: .` membangun image dari Dockerfile di folder ini.
- `ports: "8000:8000"` memetakan port komputer ke port container.
- `TUGASKU_SECRET_KEY: ${TUGASKU_SECRET_KEY:?...}` mengambil nilai dari environment mesin atau berkas `.env` di sebelah `docker-compose.yml`, dan **gagal dengan pesan** bila kosong. Rahasia tidak ditulis di berkas.
- `volumes: tugasku-data:/data` memasang volume bernama ke `/data`.
- `restart: unless-stopped` menyalakan ulang container bila mati (kecuali dihentikan manual).

## Menjalankan

Semua perintah dijalankan dari `examples/fastapi/proyek/tahap-6`.

```bash
# 1. Bangun image
docker build -t tugasku:1.0 .

# 2. Siapkan berkas rahasia (tidak di-commit): salin .env.contoh menjadi .env,
#    lalu isi TUGASKU_SECRET_KEY dengan kunci acak (cara membuatnya ada di halaman Token)
cp .env.contoh .env

# 3. Jalankan migrasi sekali, pada volume yang sama dengan aplikasi
docker run --rm --env-file .env -v tugasku-data:/data -w /data tugasku:1.0 alembic -c /code/alembic.ini upgrade head

# 4. Jalankan aplikasi
docker run -d --name tugasku --env-file .env -p 8000:8000 -v tugasku-data:/data tugasku:1.0

# 5. Periksa
curl http://127.0.0.1:8000/kesehatan
```

Di Windows PowerShell, ganti `cp` dengan `Copy-Item` dan `curl` dengan `curl.exe`. Perintah `docker` sama. (Perintah Windows tidak diuji; pengujian di Ubuntu.)

Catatan atas perintah:

- `-v tugasku-data:/data` memasang volume bernama; Docker membuatnya bila belum ada.
- `-w /data` menjalankan migrasi dari folder data, sehingga `alembic.ini` (yang berisi `sqlite:///database.db`, jalur relatif) menulis ke `/data/database.db`, berkas yang sama dengan yang dipakai aplikasi lewat `TUGASKU_DATABASE_URL`.
- `--env-file .env` memberi rahasia tanpa menuliskannya di perintah (yang akan tersimpan di riwayat shell).
- `.env.contoh` mengisi `TUGASKU_LINGKUNGAN=produksi`, sehingga `/docs` ditutup. Karena itu langkah 5 memakai `/kesehatan`, bukan `/docs`.
- Dengan Compose: `docker compose up -d --build`, dan migrasi dengan `docker compose run --rm -w /data api alembic -c /code/alembic.ini upgrade head`.
- Urutan migrasi lalu aplikasi sesuai anjuran dokumentasi FastAPI: langkah sebelum aplikasi (seperti migrasi) dijalankan sebelum proses utama, atau sebagai container terpisah pada pengaturan multi-container.
- Membersihkan setelah selesai: `docker rm -f tugasku`, `docker volume rm tugasku-data`, `docker rmi tugasku:1.0`.

## Yang sudah diuji

Semua baris berikut berasal dari eksekusi nyata di Ubuntu (Docker Engine 29.9.2, Compose 5.6.1), memakai salinan folder `tahap-6` dengan `.env` berisi kunci acak 64 karakter, `TUGASKU_LINGKUNGAN=produksi`, `TUGASKU_ORIGIN_DIIZINKAN=["https://tugasku.contoh"]`, dan `TUGASKU_LOG_FORMAT=json`. Karena port 8000 di mesin penguji sudah terpakai, pemetaan port yang diuji adalah `18000:8000`, bukan `8000:8000`.

| Langkah | Hasil |
|---|---|
| `docker build -t tugasku:1.0 .` | berhasil; `docker images` menampilkan ukuran **1,8 GB** (image dasar `python:3.14` yang penuh) |
| Migrasi dengan `docker run --rm ... alembic ... upgrade head` | kedua revisi berjalan (`buat tabel kategori dan tugas`, `tambah pengguna dan pemilik tugas`) |
| `docker run -d ...` | log: `Starting FastAPI in production mode`, `Using import string: app.main:app`, `Server started at http://0.0.0.0:8000`, `Uvicorn running on http://0.0.0.0:8000` |
| `GET /kesehatan` dari komputer lewat `-p` | `200`, `{"status":"ok"}` |
| `GET /siap` | `200`, `{"status":"siap"}` |
| `GET /docs` | `404` (ditutup di produksi) |
| `POST /daftar` (pengguna `budi`) | `201`, `{"id":1,"nama_pengguna":"budi","peran":"anggota"}` |
| `docker exec tugasku id` | `uid=1000(aplikasi) gid=1000(aplikasi)`: bukan root |
| `/data` di dalam container | dimiliki `aplikasi`; `database.db` ada di dalamnya |
| Container dihapus lalu dibuat lagi pada volume yang sama, `POST /daftar` `budi` lagi | `409 NAMA_PENGGUNA_SUDAH_ADA`: data bertahan di volume |
| `docker stop` | selesai dalam sekitar 0,5 detik, kode keluar `0`; log: `Shutting down`, `Waiting for application shutdown`, `Application shutdown complete` |
| `docker compose config` tanpa `TUGASKU_SECRET_KEY` | gagal dengan pesan `required variable TUGASKU_SECRET_KEY is missing a value: TUGASKU_SECRET_KEY belum diisi` |
| `docker compose up -d --build` dengan `.env`, lalu migrasi lewat `docker compose run --rm -w /data api ...` | container `Up`; `GET /siap` `200`; `POST /daftar` `201` |
| `docker compose down -v` | container, jaringan, dan volume Compose terhapus |

Jadi `Dockerfile`, `.env.contoh`, urutan migrasi lalu aplikasi, pemetaan port, volume, pengguna non-root, penghentian baik-baik, dan sintaks `${VAR:?pesan}` terbukti bekerja pada mesin dan versi di atas. Dari pengujian ini, `fastapi run` pada `0.0.0.0` di dalam container memang terjangkau dari luar lewat `-p`.

Catatan: pada pengujian Compose, aplikasi dinyalakan sebelum migrasi dijalankan. Aplikasi tidak gagal, dan `/siap` menjawab `200` karena `/siap` hanya memeriksa bahwa basis data bisa dijangkau, bukan bahwa tabelnya sudah ada. Jalankan migrasi lebih dulu seperti di urutan di atas.

### Yang belum diuji

- Isi image: **tidak diperiksa** apakah `.env`, `*.db`, atau `tests/` benar-benar tidak ikut tersalin. Pengecualian di `.dockerignore` tidak diverifikasi langsung.
- Waktu build, perilaku cache lapisan, dan perbandingan ukuran dengan image `slim`.
- `restart: unless-stopped` (tidak ada container yang dimatikan paksa untuk melihat penyalaan ulang).
- Volume yang dipasang sebagai bind mount, termasuk hak tulis `/data`.
- Docker Desktop di Windows dan macOS, dan perintah PowerShell di halaman ini.
- Bentuk *shell* pada `CMD` (hanya bentuk exec yang dicoba).
- Pemindaian kerentanan image.
- Basis data selain SQLite.
- Proksi dan HTTPS di depan container: lihat [Reverse Proxy dan HTTPS](reverse-proxy-https.md).

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Menanam rahasia di `Dockerfile` atau `ENV` | Rahasia tersimpan di image dan bisa dibaca siapa saja yang memegang image. Berikan saat dijalankan. |
| `CMD fastapi run ...` tanpa tanda kurung siku (bentuk shell) | Menurut dokumentasi FastAPI, penghentian tidak baik-baik dan `lifespan` tidak berjalan semestinya. Tidak diuji. |
| Menyalin seluruh folder sebelum memasang dependensi | Cache lapisan dependensi rusak tiap kode berubah; build jadi lambat. Tidak diukur. |
| SQLite di dalam container tanpa volume | Data hilang bila container dihapus atau diganti. |
| Lupa `.dockerignore` | `.env`, `*.db`, atau `.venv` bisa ikut masuk image. |
| Memakai `--workers` di container pada Kubernetes | Dokumentasi FastAPI menyarankan satu proses per container. |
| Migrasi ke basis data yang berbeda dari yang dipakai aplikasi | Aplikasi gagal karena tabel tidak ada. Pastikan URL dan jalur sama (di sini lewat `-w /data` dan `/data`). |
| Menjalankan sebagai `root` | Dampak eksploitasi lebih besar. |
| Mengunci tag `latest` | Build tidak terulang. Gunakan tag versi (`python:3.14`, `tugasku:1.0`). |
| Menganggap hasil uji di Linux berlaku di mana saja | Hanya Ubuntu dengan Docker Engine yang dicoba; Docker Desktop belum. |

## Latihan

1. **Dasar.** Apa beda image dan container?
2. **Analisis.** Mengapa `COPY ./requirements.txt` ditaruh sebelum `COPY ./app`?
3. **Prediksi.** Apa yang terjadi pada data bila container dihapus dengan `docker rm`, dengan dan tanpa volume `tugasku-data`?
4. **Keamanan.** Mengapa `TUGASKU_SECRET_KEY` tidak ditulis di `Dockerfile`?

??? success "Kunci jawaban"
    Jawaban 3 untuk kasus dengan volume mengacu pada hasil uji nyata (container dihapus lalu dibuat lagi, data bertahan). Kasus tanpa volume adalah penalaran yang tidak diuji. Jawaban 1, 2, dan 4 adalah penjelasan dari dokumentasi dan penalaran dari isi halaman.

    1. Image adalah paket tetap yang berisi aplikasi dan lingkungannya (hasil `docker build`). Container adalah image yang sedang berjalan; satu image bisa melahirkan banyak container.
    2. Daftar dependensi jarang berubah, sedangkan kode sering berubah. Dengan menyalin `requirements.txt` dan memasangnya lebih dulu, Docker bisa memakai ulang lapisan dependensi pada build berikutnya selama `requirements.txt` sama, dan hanya membangun ulang lapisan kode.
    3. Dengan volume: data ada di volume, jadi tetap ada setelah container dihapus (diuji: pendaftaran `budi` ditolak `409` setelah container dibuat ulang). Tanpa volume: data berada di sistem berkas container dan ikut hilang bersama container (penalaran dari cara kerja Docker; tidak diuji).
    4. Karena isi image bisa dibaca siapa pun yang memilikinya, dan Dockerfile biasanya masuk Git. Rahasia diberikan saat dijalankan (`--env-file` atau environment Compose).

## Ringkasan

- Container mengemas aplikasi beserta lingkungannya; image dibangun dari Dockerfile, container adalah image yang berjalan.
- Dockerfile FastAPI: image Python resmi, `requirements.txt` lebih dulu, kode kemudian, `CMD` bentuk exec dengan `fastapi run`, satu proses per container.
- Data SQLite disimpan di volume (`/data`), dan migrasi dijalankan pada volume yang sama.
- Rahasia tidak ditanam di image; berikan lewat `--env-file` atau environment Compose.
- `.dockerignore` mencegah rahasia dan data ikut ke image.
- Dockerfile dan Compose di halaman ini sudah dibangun dan dijalankan di Ubuntu dengan Docker Engine 29.9.2; bagian yang belum diuji dicatat di atas.

## Langkah berikutnya

Lanjut ke [Variabel Environment di Produksi](variabel-environment.md); health check dan HTTPS di depan container dibahas di [Reverse Proxy dan HTTPS](reverse-proxy-https.md), atau kembali ke daftar materi di [Modul 10: Deployment](index.md).
