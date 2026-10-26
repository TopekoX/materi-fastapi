# Proyek: Memecah TugasKu

## Tujuan pembelajaran

Setelah mengerjakan halaman ini, kamu mampu:

- [ ] Memecah aplikasi yang sudah berjalan menjadi paket berisi beberapa modul tanpa mengubah perilakunya.
- [ ] Menentukan tanggung jawab tiap berkas: konfigurasi, basis data, error, keamanan, model, dan router.
- [ ] Memindahkan konfigurasi dari kode ke `pydantic-settings`.
- [ ] Mendaftarkan exception handler dari fungsi terpisah.
- [ ] Membuktikan bahwa perilaku API setelah refaktor sama dengan sebelumnya.

## Prasyarat

- Sudah mengerjakan [Proyek Praktik Tahap 4](../07-autentikasi-keamanan/proyek-tahap-4.md).
- Sudah membaca [Router Modular](router-modular.md), [Konfigurasi dan Environment](konfigurasi-environment.md), [Middleware](middleware.md), dan [Lifespan](lifespan.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **SQLModel 0.0.48**, **Alembic 1.20.1**, **PyJWT 2.15.1**, **pwdlib 0.3.1**, dan **pydantic-settings 2.16.1** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

!!! note "Halaman ini bukan tahap proyek baru"
    PRD (§7) tidak menetapkan tahap proyek untuk Modul 08. Halaman ini adalah **refaktor** dari tahap 4: fitur dan perilaku API sama, hanya strukturnya yang berubah. Kodenya ada di `examples/fastapi/proyek/tahap-4-modular/`, dan menjadi dasar yang rapi untuk tahap 5 (pengujian) di Modul 09.

## Tentang refaktor ini

**Refaktor** berarti mengubah struktur kode tanpa mengubah perilakunya. Tahap 4 ditulis di satu `main.py` sepanjang 322 baris, ditambah `models.py`. Kini dipecah berdasarkan tanggung jawab:

| Berkas | Baris | Tanggung jawab |
|---|---|---|
| `app/config.py` | 21 | Konfigurasi (`pydantic-settings`) |
| `app/database.py` | 17 | Engine dan session |
| `app/models.py` | 81 | Model tabel dan skema (tidak berubah dari tahap 4) |
| `app/errors.py` | 71 | Exception dan handler |
| `app/keamanan.py` | 58 | Hashing, token, dan dependency autentikasi dan otorisasi |
| `app/routers/auth.py` | 50 | `/daftar`, `/token`, `/saya` |
| `app/routers/kategori.py` | 22 | Endpoint kategori |
| `app/routers/tugas.py` | 110 | Endpoint tugas |
| `app/main.py` | 23 | Merakit aplikasi |

Total baris bertambah (453 dibanding 403) karena impor di tiap berkas, tetapi tiap berkas pendek dan punya satu alasan untuk diubah.

### Struktur folder

```text
tahap-4-modular/
├── alembic.ini
├── alembic/
├── buat_pengelola.py
└── app/
    ├── __init__.py
    ├── main.py
    ├── config.py
    ├── database.py
    ├── models.py
    ├── errors.py
    ├── keamanan.py
    └── routers/
        ├── __init__.py
        ├── auth.py
        ├── kategori.py
        └── tugas.py
```

### Peta pemindahan dari tahap 4

| Di tahap 4 (`main.py`) | Sekarang |
|---|---|
| `SECRET_KEY = os.environ.get(...)`, `ALGORITMA`, `MENIT_KEDALUWARSA`, `ORIGIN_DIIZINKAN` | `Settings` di `config.py` |
| `engine`, `get_session`, `SessionDep` | `database.py` |
| Kelas exception, `respons_galat`, dan semua `@app.exception_handler` | `errors.py` (handler didaftarkan lewat fungsi) |
| `password_hash`, `buat_token`, `pengguna_saat_ini`, `wajib_pengelola` | `keamanan.py` |
| `/daftar`, `/token`, `/saya` | `routers/auth.py` |
| Endpoint kategori | `routers/kategori.py` |
| Fungsi pembantu dan endpoint tugas | `routers/tugas.py` |
| `FastAPI(...)`, `CORSMiddleware`, dan perakitan | `main.py` |

## Kode lengkap

### `app/config.py`

```python title="app/config.py"
--8<-- "fastapi/proyek/tahap-4-modular/app/config.py"
```

### `app/database.py`

```python title="app/database.py"
--8<-- "fastapi/proyek/tahap-4-modular/app/database.py"
```

### `app/errors.py`

```python title="app/errors.py"
--8<-- "fastapi/proyek/tahap-4-modular/app/errors.py"
```

### `app/keamanan.py`

```python title="app/keamanan.py"
--8<-- "fastapi/proyek/tahap-4-modular/app/keamanan.py"
```

### `app/routers/auth.py`

```python title="app/routers/auth.py"
--8<-- "fastapi/proyek/tahap-4-modular/app/routers/auth.py"
```

### `app/routers/kategori.py`

```python title="app/routers/kategori.py"
--8<-- "fastapi/proyek/tahap-4-modular/app/routers/kategori.py"
```

### `app/routers/tugas.py`

```python title="app/routers/tugas.py"
--8<-- "fastapi/proyek/tahap-4-modular/app/routers/tugas.py"
```

### `app/main.py`

```python title="app/main.py"
--8<-- "fastapi/proyek/tahap-4-modular/app/main.py"
```

`app/models.py` identik dengan `models.py` di tahap 4 (lihat [halaman tahap 4](../07-autentikasi-keamanan/proyek-tahap-4.md)), jadi tidak diulang di sini. `buat_pengelola.py` dan migrasi Alembic juga sama, dengan penyesuaian impor yang dijelaskan di bawah.

## Penjelasan kode

### Konfigurasi terpusat

`Settings` di `config.py` menggantikan nilai yang sebelumnya tersebar: kunci penandatangan, algoritma, masa berlaku (kini `detik_akses`), daftar origin, dan alamat basis data. `get_settings()` memakai `@lru_cache` sehingga dibaca sekali. Perubahan penting: nama variabel kunci kini **`TUGASKU_SECRET_KEY`** (berawalan `TUGASKU_`), bukan `SECRET_KEY` seperti di tahap 4. Kunci memakai `SecretStr`, sehingga nilainya dibaca dengan `.get_secret_value()` di `keamanan.py`.

### Basis data di satu tempat

`database.py` membuat `engine` dari `settings.database_url` dan menyediakan `SessionDep`. Router mengimpornya dari sini, bukan membuat sendiri.

### Error di satu tempat

`errors.py` berisi kelas exception dan `respons_galat`. Handler tidak lagi didekorasi dengan `@app.exception_handler` di tingkat modul (karena `app` belum ada di sini), tetapi didaftarkan lewat fungsi:

```python
def pasang_penangan_error(app: FastAPI) -> None:
    @app.exception_handler(TugasTidakDitemukan)
    async def tugas_tidak_ditemukan(request, exc): ...
```

`main.py` memanggil `pasang_penangan_error(app)`. Pola "fungsi yang memasang sesuatu ke aplikasi" membuat modul tidak perlu mengimpor `app`.

### Keamanan sebagai modul

`keamanan.py` mengumpulkan hashing, pembuatan dan verifikasi token, serta dependency `PenggunaLogin` dan `Pengelola`. Router tinggal mengimpor alias ini. Dependency yang dulu didefinisikan di tengah berkas besar kini mudah ditemukan.

### Router dengan path yang sama

```python
router = APIRouter(prefix="/tugas", tags=["tugas"])

@router.post("", ...)
```

Endpoint memakai path `""` (kosong) bersama `prefix`, sehingga URL tetap `/tugas` dan `/kategori`, persis seperti di tahap 4. Menulis `"/"` akan mengubah URL menjadi `/tugas/` (lihat pengalihan `307` di [Router Modular](router-modular.md)).

### Perakitan di `main.py`

`main.py` hanya merakit: membuat `FastAPI`, memasang `CORSMiddleware` dari konfigurasi, mendaftarkan handler error, dan menyertakan tiga router. Ia tidak berisi logika bisnis.

### Alembic dan impor

Di `alembic/env.py`, impor model berubah dari `import models` menjadi `from app import models`, karena modelnya kini ada di paket `app`. Alembic hanya mengimpor `app.models`, bukan seluruh aplikasi, sehingga perintah `alembic` **tidak membutuhkan** `TUGASKU_SECRET_KEY` (teruji). Alamat basis data di `alembic.ini` (`sqlite:///database.db`) harus sejalan dengan `database_url` di `config.py`; keduanya sama di contoh ini, tetapi disimpan di dua tempat.

### `buat_pengelola.py`

Skrip kini mengimpor `engine` dan `password_hash` dari paket `app`, sehingga memakai konfigurasi yang sama dengan aplikasi. Karena `app.database` memanggil `get_settings()` saat diimpor, skrip ini **membutuhkan** `TUGASKU_SECRET_KEY` terisi.

## Menjalankan

Dari folder `tahap-4-modular/`:

```powershell
pip install "fastapi[standard]" sqlmodel alembic pyjwt "pwdlib[argon2]" pydantic-settings
$env:TUGASKU_SECRET_KEY = (python -c "import secrets; print(secrets.token_hex(32))")
alembic upgrade head
python buat_pengelola.py rina "sandi-rina-789"
fastapi dev app/main.py
```

Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah. Kata sandi `sandi-rina-789` hanya contoh.

## Membuktikan perilaku sama

Hasil di bawah dijalankan dengan `curl.exe` dari basis data baru (hasil `alembic upgrade head`) dengan `rina` sebagai pengelola. Hasilnya sama dengan yang dicatat di [tahap 4](../07-autentikasi-keamanan/proyek-tahap-4.md), kecuali nomor `id` yang bergeser satu karena tidak ada tugas lama dari tahap 3.

| Request | Status | Isi |
|---|---|---|
| `POST /daftar` `budi` | `201` | `{"id":2,"nama_pengguna":"budi","peran":"anggota"}` |
| `POST /daftar` `budi` (ulang) | `409` | `NAMA_PENGGUNA_SUDAH_ADA` |
| `POST /token` kata sandi salah | `401` | `HTTP_401`, header `www-authenticate: Bearer` |
| `GET /tugas` tanpa token | `401` | `Not authenticated` |
| `POST /kategori` oleh `budi` | `403` | `Hanya untuk pengelola` |
| `POST /kategori` oleh `rina` | `201` | `{"nama":"Kuliah","id":1}` |
| `budi` `POST /tugas` "Belajar FastAPI" | `201` | tugas `id` 1, `"pemilik_id":2` |
| `budi` `POST /tugas` "belajar fastapi" | `409` | `JUDUL_SUDAH_ADA` |
| `sari` `POST /tugas` "belajar fastapi" | `201` | `id` 2, `"pemilik_id":3` |
| `budi` `POST /tugas` kategori 99 | `404` | `KATEGORI_TIDAK_ADA` |
| `GET /tugas` oleh `budi` | `200` | hanya tugas 1 |
| `GET /tugas` oleh `rina` | `200` | semua tugas |
| `sari` `GET /tugas/1` | `403` | `Tugas ini bukan milikmu` |
| `budi` `GET /tugas/1` | `200` | tugas dengan `"kategori":{"nama":"Kuliah","id":1}` |
| `budi` `PATCH /tugas/1` `{"selesai":true}` | `200` | `"selesai":true` |
| `budi` `PATCH /tugas/1` `{"judul":null}` | `400` | `Field 'judul' tidak boleh null` |
| `sari` `DELETE /tugas/1` | `403` | `Tugas ini bukan milikmu` |
| `budi` `DELETE /tugas/1` | `204` | tanpa isi |
| `budi` `GET /tugas/99` | `404` | `TUGAS_TIDAK_ADA` |
| `POST /tugas` data tidak valid | `422` | `VALIDASI_GAGAL` |
| Preflight CORS `OPTIONS /tugas/1` dari `http://localhost:3000` | `200` | — |

Selain itu: FastAPI CLI melaporkan `Using import string: app.main:app`; `alembic upgrade head` menjalankan kedua revisi; dan `alembic check` melaporkan `No new upgrade operations detected.`

!!! warning "Keterbatasan"
    - Pembuktian ini manual (`curl` terhadap daftar request tetap), bukan pengujian otomatis. Menggantinya dengan pengujian otomatis adalah topik Modul 09 (tahap 5).
    - Respons `500` tidak diuji ulang pada versi modular.
    - Tampilan Swagger UI, perilaku browser, dan kegagalan saat `TUGASKU_SECRET_KEY` kosong tidak diuji pada versi modular. Perilaku `Settings` sudah diuji di [Konfigurasi dan Environment](konfigurasi-environment.md).
    - Tidak ada `lifespan`: tabel dikelola Alembic, jadi tidak ada persiapan saat mulai.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Memecah sambil menambah fitur | Sulit memastikan perilaku tidak berubah. Refaktor dulu, tambah fitur kemudian. |
| Menulis path router `"/"` padahal sebelumnya `""` | URL berubah ke `/tugas/` dan klien lama mendapat pengalihan. |
| Lupa memperbarui `import models` di `alembic/env.py` | Alembic tidak menemukan model. Tidak diuji di sini. |
| Memakai nama variabel kunci lama (`SECRET_KEY`) | Konfigurasi baru mencari `TUGASKU_SECRET_KEY`. Menurut perilaku `Settings` yang diuji di halaman Konfigurasi, aplikasi menolak mulai bila kunci wajib kosong (tidak diuji ulang pada versi modular). |
| Impor melingkar antar modul | `ImportError`. Di sini dihindari dengan aliran satu arah: `config` → `database` → `models` → `keamanan` → `routers` → `main`. |
| Menaruh logika bisnis di `main.py` | Kembali menjadi berkas besar. `main.py` hanya merakit. |
| Tidak memeriksa ulang setelah memecah | Perilaku bisa berubah tanpa disadari. Jalankan kembali daftar request. |

## Latihan

1. **Dasar.** Berkas mana yang kamu ubah bila masa berlaku token diganti menjadi 10 menit?
2. **Prediksi.** Mengapa `alembic upgrade head` tidak butuh `TUGASKU_SECRET_KEY`, sedangkan `buat_pengelola.py` butuh?
3. **Praktik.** Tambahkan router `pengguna` dengan `GET /pengguna/saya`. Berkas apa yang dibuat dan diubah?
4. **Analisis.** Mengapa `pasang_penangan_error(app)` berupa fungsi, bukan dekorator di tingkat modul `errors.py`?

??? success "Kunci jawaban"
    Jawaban 2 mengacu pada hasil uji di atas. Jawaban 1, 3, dan 4 adalah penalaran dari struktur; jawaban 3 tidak dijalankan.

    1. Tidak ada berkas kode yang diubah: cukup `TUGASKU_DETIK_AKSES=600` di environment (atau `.env`), karena nilainya dibaca dari `Settings`. Syaratnya `detik_akses` minimal 60.
    2. Alembic hanya mengimpor `app.models`, yang tidak memanggil `get_settings()`. `buat_pengelola.py` mengimpor `app.database`, yang memanggil `get_settings()` saat diimpor dan butuh kunci.
    3. Buat `app/routers/pengguna.py` dengan `APIRouter(prefix="/pengguna", ...)` dan endpoint `GET /saya` memakai `PenggunaLogin`, lalu tambahkan `from .routers import pengguna` dan `app.include_router(pengguna.router)` di `main.py`.
    4. Dekorator `@app.exception_handler(...)` butuh objek `app`, yang dibuat di `main.py`. Dengan fungsi yang menerima `app`, `errors.py` tidak perlu mengimpor `main.py` (yang akan membuat impor melingkar).

## Ringkasan

- Refaktor mengubah struktur tanpa mengubah perilaku; bukti perilaku sama adalah menjalankan kembali daftar request yang sama.
- Pecah berdasarkan tanggung jawab: konfigurasi, basis data, error, keamanan, model, router, dan `main.py` yang hanya merakit.
- Konfigurasi dipindah ke `pydantic-settings`; kuncinya kini `TUGASKU_SECRET_KEY`.
- Handler error dipasang lewat fungsi agar tidak ada impor melingkar.
- Path router kosong (`""`) menjaga URL tetap sama dengan sebelum dipecah.
- Alembic mengimpor model dari paket `app` dan tidak membutuhkan konfigurasi rahasia.

## Langkah berikutnya

Kembali ke daftar materi di [Modul 08: Struktur Proyek](index.md). Modul berikutnya adalah [Modul 09: Pengujian](../09-pengujian/index.md), tempat struktur ini dipakai untuk menulis pengujian otomatis.
