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
- Sudah mengerjakan [Proyek Praktik Tahap 5](../09-pengujian/proyek-tahap-5.md). Dockerfile di halaman ini mengemas aplikasi itu.

!!! info "Versi yang diuji"
    Langkah yang bisa diemulasikan dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **FastAPI CLI 0.0.32**, **Uvicorn 0.54.0**, **SQLModel 0.0.48**, dan **Alembic 1.20.1** di Windows. Docker yang terpasang di mesin penulis: **Docker 29.2.1**. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini).

!!! danger "Dockerfile di halaman ini BELUM dibangun atau dijalankan"
    Docker terpasang di mesin penulis, tetapi *daemon*-nya tidak berjalan (`docker info`: gagal terhubung ke API Docker). Menyalakan Docker Desktop dan mengunduh image dasar adalah tindakan di luar repositori yang tidak dilakukan tanpa izin. Akibatnya **tidak ada perintah `docker build` atau `docker run` yang dijalankan**, dan tidak ada keluaran Docker di halaman ini yang berasal dari eksekusi nyata. Sebagai gantinya, isi Dockerfile **diemulasikan** langkah demi langkah di luar Docker (lihat [bagian emulasi](#yang-sudah-diuji-emulasi-tanpa-docker)). Itu membuktikan dependensi dan perintahnya benar, tetapi **bukan** bahwa image-nya terbangun. Bacalah semua perintah `docker` di sini sebagai rancangan yang belum terverifikasi.

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

Berkas ada di `examples/fastapi/10-deployment/container/`. Salin keempatnya ke **akar proyek** yang berisi `app/`, `alembic/`, dan `alembic.ini` (yaitu proyek tahap 5).

### `Dockerfile`

```dockerfile title="Dockerfile"
--8<-- "fastapi/10-deployment/container/Dockerfile"
```

### `requirements.txt`

```text title="requirements.txt"
--8<-- "fastapi/10-deployment/container/requirements.txt"
```

Hanya dependensi untuk menjalankan aplikasi. `pytest` dan `pytest-cov` tidak dimasukkan, karena image produksi tidak perlu menjalankan pengujian.

### `.dockerignore`

```text title=".dockerignore"
--8<-- "fastapi/10-deployment/container/.dockerignore"
```

### `docker-compose.yml`

```yaml title="docker-compose.yml"
--8<-- "fastapi/10-deployment/container/docker-compose.yml"
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

## Perintah yang dirancang (belum dijalankan)

```powershell
# 1. Bangun image
docker build -t tugasku:1.0 .

# 2. Siapkan berkas rahasia (tidak di-commit): TUGASKU_SECRET_KEY=<kunci acak>
#    (cara membuat kunci ada di halaman Token)

# 3. Jalankan migrasi sekali, pada volume yang sama dengan aplikasi
docker run --rm --env-file .env -v tugasku-data:/data -w /data tugasku:1.0 alembic -c /code/alembic.ini upgrade head

# 4. Jalankan aplikasi
docker run -d --name tugasku --env-file .env -p 8000:8000 -v tugasku-data:/data tugasku:1.0

# 5. Periksa
curl.exe http://127.0.0.1:8000/docs
```

Catatan atas perintah:

- `-v tugasku-data:/data` memasang volume bernama; Docker membuatnya bila belum ada.
- `-w /data` menjalankan migrasi dari folder data, sehingga `alembic.ini` (yang berisi `sqlite:///database.db`, jalur relatif) menulis ke `/data/database.db`, berkas yang sama dengan yang dipakai aplikasi lewat `TUGASKU_DATABASE_URL`.
- `--env-file .env` memberi rahasia tanpa menuliskannya di perintah (yang akan tersimpan di riwayat shell).
- Dengan Compose: `docker compose up --build`, dan migrasi dengan `docker compose run --rm -w /data api alembic -c /code/alembic.ini upgrade head`. Kedua perintah ini juga belum dijalankan.
- Urutan migrasi lalu aplikasi sesuai anjuran dokumentasi FastAPI: langkah sebelum aplikasi (seperti migrasi) dijalankan sebelum proses utama, atau sebagai container terpisah pada pengaturan multi-container.

## Yang sudah diuji (emulasi tanpa Docker)

Isi Dockerfile ditiru langkah demi langkah di luar Docker: sebuah folder `code/` (isi `/code`) dan folder `data/` (isi `/data`), serta venv baru. Perintah dan lingkungan mengikuti Dockerfile.

| Langkah Dockerfile | Emulasi | Hasil |
|---|---|---|
| `pip install -r requirements.txt` | venv bersih dari `requirements.txt` yang sama | berhasil; FastAPI 0.162.0, FastAPI CLI 0.0.32, Uvicorn 0.54.0, SQLModel 0.0.48, Alembic 1.20.1, PyJWT 2.15.1, pwdlib 0.3.1, pydantic-settings 2.16.1, python-multipart 0.0.32, httpx 0.28.1 |
| migrasi: `alembic -c /code/alembic.ini upgrade head` dari folder `data/` dengan `PYTHONPATH=code` | dijalankan dari folder data | kedua revisi berjalan; `database.db` terbentuk **di folder data** |
| `CMD fastapi run app/main.py ...` dengan `TUGASKU_DATABASE_URL` mengarah ke folder data | dijalankan dari folder code, `--host 127.0.0.1` | `Using import string: app.main:app`, `Server started`, `Uvicorn running` |
| `POST /daftar` | `curl.exe` | `201`, `{"id":1,"nama_pengguna":"budi","peran":"anggota"}` |
| `GET /docs` | `curl.exe` | `200` |
| Proses dihentikan lalu dijalankan lagi (meniru restart container pada volume yang sama) | mendaftarkan `budi` lagi | `409` `NAMA_PENGGUNA_SUDAH_ADA`: data bertahan |
| Tanpa `TUGASKU_SECRET_KEY` | menjalankan `fastapi run` | `ValidationError` untuk `secret_key` (`Field required`); aplikasi tidak mulai |

Jadi urutan perintah, dependensi, jalur impor, dan perilaku konfigurasi terbukti benar. Karena emulasi dijalankan dengan `--host 127.0.0.1`, **tidak** terbukti bahwa `fastapi run` pada `0.0.0.0` di dalam container terjangkau dari luar lewat `-p`.

### Yang belum diuji

- `docker build`: sintaks Dockerfile, ketersediaan image `python:3.14`, dan apakah semua `COPY` menemukan berkasnya.
- `RUN useradd` dan `USER aplikasi`: termasuk hak tulis di `/data` pada volume bernama, dan perilaku bila volume dipasang dari bind mount.
- `docker run`, pemetaan port `-p`, `-w /data`, dan `--env-file`.
- Docker Compose, `restart`, dan sintaks `${VAR:?pesan}`.
- Pengecualian di `.dockerignore`.
- Ukuran image, waktu build, dan perilaku cache lapisan.
- Penghentian baik-baik (`docker stop` mengirim sinyal ke proses 1) serta kode `lifespan` yang berjalan saat berhenti.
- Penggunaan proksi di depan container.

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
| Menganggap Dockerfile ini sudah teruji | Belum dibangun (lihat peringatan di atas). |

## Latihan

1. **Dasar.** Apa beda image dan container?
2. **Analisis.** Mengapa `COPY ./requirements.txt` ditaruh sebelum `COPY ./app`?
3. **Prediksi.** Apa yang terjadi pada data bila container dihapus dengan `docker rm`, dengan dan tanpa volume `tugasku-data`?
4. **Keamanan.** Mengapa `TUGASKU_SECRET_KEY` tidak ditulis di `Dockerfile`?

??? success "Kunci jawaban"
    Jawaban 3 sebagian mengacu pada hasil emulasi (data bertahan di folder data walau proses diganti) dan sebagian penalaran tentang volume Docker yang tidak diuji. Jawaban 1, 2, dan 4 adalah penjelasan dari dokumentasi dan penalaran dari isi halaman.

    1. Image adalah paket tetap yang berisi aplikasi dan lingkungannya (hasil `docker build`). Container adalah image yang sedang berjalan; satu image bisa melahirkan banyak container.
    2. Daftar dependensi jarang berubah, sedangkan kode sering berubah. Dengan menyalin `requirements.txt` dan memasangnya lebih dulu, Docker bisa memakai ulang lapisan dependensi pada build berikutnya selama `requirements.txt` sama, dan hanya membangun ulang lapisan kode.
    3. Dengan volume: data ada di volume, jadi tetap ada setelah container dihapus (dalam emulasi, data tetap ada ketika proses diganti). Tanpa volume: data berada di sistem berkas container dan ikut hilang bersama container (penalaran dari cara kerja Docker; tidak diuji).
    4. Karena isi image bisa dibaca siapa pun yang memilikinya, dan Dockerfile biasanya masuk Git. Rahasia diberikan saat dijalankan (`--env-file` atau environment Compose).

## Ringkasan

- Container mengemas aplikasi beserta lingkungannya; image dibangun dari Dockerfile, container adalah image yang berjalan.
- Dockerfile FastAPI: image Python resmi, `requirements.txt` lebih dulu, kode kemudian, `CMD` bentuk exec dengan `fastapi run`, satu proses per container.
- Data SQLite disimpan di volume (`/data`), dan migrasi dijalankan pada volume yang sama.
- Rahasia tidak ditanam di image; berikan lewat `--env-file` atau environment Compose.
- `.dockerignore` mencegah rahasia dan data ikut ke image.
- **Dockerfile di halaman ini belum dibangun**; yang terbukti hanyalah isinya lewat emulasi tanpa Docker.

## Langkah berikutnya

Lanjut ke [Variabel Environment di Produksi](variabel-environment.md), atau kembali ke daftar materi di [Modul 10: Deployment](index.md).
