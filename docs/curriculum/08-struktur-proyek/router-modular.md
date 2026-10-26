# Router Modular

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan mengapa aplikasi besar perlu dipecah ke beberapa berkas.
- [ ] Menyusun struktur folder paket Python untuk aplikasi FastAPI.
- [ ] Membuat `APIRouter` di berkas terpisah dan memasangnya dengan `include_router`.
- [ ] Menggunakan impor relatif dan memahami mengapa `__init__.py` diperlukan.
- [ ] Mengatur `prefix`, `tags`, dan `dependencies` di tingkat router maupun saat `include_router`.
- [ ] Menjalankan aplikasi yang terdiri dari paket.

## Prasyarat

- Sudah membaca [Dependency per Router](../05-dependency-injection/dependency-router.md). Halaman itu memperkenalkan `APIRouter` dengan semua kode dalam satu berkas.
- Paham `import` di Python, termasuk modul dan paket (folder dengan `__init__.py`).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7** dan **FastAPI 0.162.0** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

### Masalah: satu berkas yang membengkak

Proyek [tahap 4](../07-autentikasi-keamanan/proyek-tahap-4.md) menaruh konfigurasi, penanganan error, autentikasi, dan semua endpoint dalam satu `main.py` sepanjang ratusan baris. Semakin besar aplikasi, semakin sulit menemukan sesuatu, dan semakin besar kemungkinan dua orang mengubah berkas yang sama.

Solusinya: pecah berdasarkan **tanggung jawab**. Endpoint tugas di satu berkas, endpoint kategori di berkas lain, dan seterusnya. FastAPI menyediakan `APIRouter` untuk itu. Seperti dijelaskan di Modul 05, `APIRouter` adalah "FastAPI mini" yang punya `prefix`, `tags`, dan `dependencies` sendiri, lalu dipasang ke aplikasi utama dengan `include_router`.

### Struktur folder

Contoh di halaman ini memakai struktur berikut (di `examples/fastapi/08-struktur-proyek/router-modular/`):

```text
router-modular/
└── app/
    ├── __init__.py
    ├── main.py
    ├── dependencies.py
    ├── schemas.py
    └── routers/
        ├── __init__.py
        ├── tugas.py
        ├── kategori.py
        └── admin.py
```

| Berkas | Tanggung jawab |
|---|---|
| `main.py` | Membuat `FastAPI` dan memasang router |
| `dependencies.py` | Dependency yang dipakai banyak router |
| `schemas.py` | Model Pydantic (skema input dan output) |
| `routers/tugas.py` | Endpoint tugas |
| `routers/kategori.py` | Endpoint kategori |
| `routers/admin.py` | Endpoint khusus pengelola |
| `__init__.py` (dua berkas) | Menandai folder sebagai **paket** Python; boleh kosong |

Pada contoh ini data disimpan di `dict` di memori agar fokus ke struktur. Tidak ada basis data atau autentikasi sungguhan: `dependencies.py` memakai header `X-Pengguna` buatan sendiri sebagai pengganti sementara, seperti di Modul 05.

### Impor relatif

Di dalam paket, berkas saling mengimpor dengan **impor relatif**:

| Penulisan | Artinya |
|---|---|
| `from .dependencies import ...` | dari berkas `dependencies.py` di folder yang sama |
| `from ..dependencies import ...` | dari satu folder di atas |
| `from . import kategori, tugas` | modul `kategori` dan `tugas` di folder yang sama |

Satu titik berarti "folder ini", dua titik berarti "folder induk".

## Kode lengkap

### `app/main.py`

```python title="app/main.py"
--8<-- "fastapi/08-struktur-proyek/router-modular/app/main.py"
```

### `app/routers/tugas.py`

```python title="app/routers/tugas.py"
--8<-- "fastapi/08-struktur-proyek/router-modular/app/routers/tugas.py"
```

### `app/routers/kategori.py`

```python title="app/routers/kategori.py"
--8<-- "fastapi/08-struktur-proyek/router-modular/app/routers/kategori.py"
```

### `app/routers/admin.py`

```python title="app/routers/admin.py"
--8<-- "fastapi/08-struktur-proyek/router-modular/app/routers/admin.py"
```

### `app/dependencies.py`

```python title="app/dependencies.py"
--8<-- "fastapi/08-struktur-proyek/router-modular/app/dependencies.py"
```

### `app/schemas.py`

```python title="app/schemas.py"
--8<-- "fastapi/08-struktur-proyek/router-modular/app/schemas.py"
```

## Penjelasan kode

### Router di berkas sendiri

```python
router = APIRouter(
    prefix="/tugas",
    tags=["tugas"],
    responses={404: {"description": "Tugas tidak ditemukan"}},
)
```

- `prefix="/tugas"` ditambahkan di depan setiap path di router ini. Endpoint `"/"` menjadi `/tugas/`, dan `"/{tugas_id}"` menjadi `/tugas/{tugas_id}`. Prefix tidak boleh diakhiri `/`.
- `tags=["tugas"]` mengelompokkan endpoint di dokumentasi.
- `responses` mendokumentasikan respons `404` untuk semua endpoint di router ini.
- Endpoint memakai `@router.get(...)`, bukan `@app.get(...)`. Berkas ini tidak tahu apa pun tentang `app`.

### Impor relatif di router

```python
from ..dependencies import pengguna_saat_ini
from ..schemas import Tugas, TugasBuat
```

`tugas.py` berada di `app/routers/`, jadi `..` naik ke `app/`. Dependency dan skema dipakai bersama, sehingga ditaruh di `app/`, bukan diulang di tiap router.

### Memasang router di `main.py`

```python
app = FastAPI(title="TugasKu API (modular)")

app.include_router(tugas.router, prefix="/api/v1")
app.include_router(kategori.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1", dependencies=[Depends(wajib_pengelola)])
```

- `include_router` memasukkan semua endpoint router ke aplikasi.
- `prefix="/api/v1"` di sini ditambahkan **di depan** prefix router. Hasilnya `/api/v1/tugas/`. Dengan begitu nomor versi API diatur di satu tempat tanpa menyentuh berkas router.
- `dependencies=[Depends(wajib_pengelola)]` pada `include_router` berlaku untuk semua endpoint router `admin`, tanpa mengubah `admin.py`. Menurut dokumentasi FastAPI, router yang sama bisa dipasang di proyek lain dengan pengaturan berbeda.

### Router yang mengakses data router lain

```python
from . import kategori, tugas
...
"jumlah_tugas": len(tugas.tugas_db),
```

`admin.py` mengimpor modul `tugas` dan `kategori` untuk membaca `tugas_db` dan `kategori_db`. Ini hanya demi contoh data di memori; pada aplikasi dengan basis data, router mengakses data lewat sesi basis data, bukan impor langsung antar router.

## Menjalankan

Jalankan dari folder `router-modular/` (induk dari `app/`):

```powershell
fastapi dev app/main.py
```

Pada pengujian, FastAPI CLI melaporkan `Using import string: app.main:app`, yaitu ia mengenali `app` sebagai paket dan memuatnya sebagai `app.main`, sehingga impor relatif berfungsi. Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah. Menjalankan `fastapi dev main.py` dari dalam folder `app/` juga memberi hasil yang sama pada pengujian (`app.main:app`).

## Mencoba request

Hasil di bawah dijalankan dengan `curl.exe`. Body JSON dikirim dari berkas dengan header `Content-Type: application/json`. Header `X-Pengguna` adalah pengganti autentikasi untuk contoh.

### Struktur path

| Request | Status | Isi |
|---|---|---|
| `GET /` | `200` | `{"pesan":"TugasKu API","versi":"v1"}` |
| `GET /api/v1/tugas/` tanpa header | `422` | `loc` `["header","x-pengguna"]`, `missing` |
| `GET /tugas/` (tanpa prefix) | `404` | `{"detail":"Not Found"}` |
| `GET /api/v1/tugas` (tanpa garis miring akhir) | `307` | `location: http://127.0.0.1:8000/api/v1/tugas/` |

Path lama tanpa `/api/v1` tidak ada lagi. Dan karena endpoint dideklarasikan sebagai `"/"` di router berprefix, path resminya berakhir dengan `/`; tanpa itu FastAPI mengalihkan (`307`).

### Router tugas

| Request | Status | Isi |
|---|---|---|
| `budi` `POST /api/v1/tugas/` `{"judul":"Belajar router modular"}` | `201` | `{"judul":"Belajar router modular","selesai":false,"id":1,"pemilik":"budi"}` |
| `budi` `GET /api/v1/tugas/` | `200` | daftar berisi tugas 1 |
| `sari` `GET /api/v1/tugas/` | `200` | `[]` |
| `sari` `GET /api/v1/tugas/1` (milik budi) | `404` | `{"detail":"Tugas tidak ditemukan"}` |

### Router kategori

| Request | Status | Isi |
|---|---|---|
| `POST /api/v1/kategori/` `{"nama":"Kuliah"}` | `201` | `{"nama":"Kuliah","id":1}` |
| `GET /api/v1/kategori/` | `200` | `[{"nama":"Kuliah","id":1}]` |
| `GET /api/v1/kategori/99` | `404` | `{"detail":"Kategori tidak ditemukan"}` |

### Router admin (dependency dari `include_router`)

| Request | Status | Isi |
|---|---|---|
| `budi` `GET /api/v1/admin/ringkasan` | `403` | `{"detail":"Hanya untuk pengelola"}` |
| `rina` `GET /api/v1/admin/ringkasan` | `200` | `{"jumlah_tugas":1,"jumlah_kategori":1}` |

Endpoint `ringkasan` tidak punya baris `Depends`, tetapi tetap dijaga oleh dependency yang dipasang saat `include_router`.

### Dokumentasi otomatis

Diuji dengan `TestClient` pada `/openapi.json`: semua path berawalan `/api/v1/`, kecuali `GET /`. Tag sesuai router: `tugas`, `kategori`, `admin`, dan `umum` untuk `GET /`. Parameter header `x-pengguna` muncul pada endpoint `tugas` dan `admin`, tidak pada endpoint `kategori`. Tampilan Swagger UI **belum diverifikasi** lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Menjalankan `python app/main.py` | Teruji: `ImportError: attempted relative import with no known parent package`. Berkas dijalankan sebagai skrip, bukan bagian paket. Jalankan lewat `fastapi dev app/main.py` atau `uvicorn app.main:app`. (Bentuk `uvicorn` tidak diuji di sini.) |
| Lupa `__init__.py` | Folder tidak dikenali sebagai paket dalam sebagian pengaturan. Tidak diuji di sini; contoh ini menyertakannya. |
| Menjalankan `fastapi dev` dari folder yang salah | Path modul tidak ditemukan. Jalankan dari folder yang berisi `app/`. |
| Lupa `include_router` | Endpoint di router tidak ada di aplikasi (404). Tidak diuji di sini. |
| Prefix dobel (mis. `/tugas` di router dan `/tugas` di endpoint) | Path menjadi `/tugas/tugas`. Pisahkan tanggung jawab: prefix di router, path relatif di endpoint. |
| Impor melingkar (`a` mengimpor `b`, `b` mengimpor `a`) | `ImportError`. Taruh kode bersama di berkas ketiga (seperti `dependencies.py`, `schemas.py`). Tidak diuji di sini. |
| Garis miring akhir tidak konsisten | `307` pada path tanpa `/` (teruji). Pilih satu gaya. |
| Mengimpor langsung data antar router di aplikasi nyata | Ketergantungan tersembunyi. Pakai basis data atau dependency. |

## Latihan

1. **Dasar.** Apa path lengkap `GET` daftar kategori? Dari mana setiap bagiannya berasal?
2. **Prediksi.** Apa yang terjadi bila `include_router(tugas.router, prefix="/api/v1")` dihapus?
3. **Praktik.** Tambahkan router `pengguna` dengan `GET /pengguna/saya` yang mengembalikan nama dari `X-Pengguna`. Berkas mana yang kamu buat dan ubah?
4. **Analisis.** Mengapa `wajib_pengelola` dipasang di `include_router` untuk router admin, bukan di `APIRouter` pada `admin.py`?

??? success "Kunci jawaban"
    Jawaban 1 dan 2 mengacu pada hasil uji di atas. Jawaban 3 adalah penerapan pola yang sama (tidak dijalankan). Jawaban 4 adalah penalaran dari penjelasan di atas.

    1. `/api/v1/kategori/`: `/api/v1` dari `include_router`, `/kategori` dari `prefix` router, dan `/` dari path endpoint.
    2. Semua endpoint tugas hilang dari aplikasi. Path `/api/v1/tugas/` menghasilkan `404`, seperti `/tugas/` yang tanpa prefix menghasilkan `404`. (Penghapusan baris itu sendiri tidak dicoba.)
    3. Buat `app/routers/pengguna.py`:

        ```python
        from typing import Annotated

        from fastapi import APIRouter, Depends

        from ..dependencies import pengguna_saat_ini

        router = APIRouter(prefix="/pengguna", tags=["pengguna"])


        @router.get("/saya")
        def saya(nama: Annotated[str, Depends(pengguna_saat_ini)]):
            return {"nama": nama}
        ```

        lalu di `main.py` tambahkan `from .routers import pengguna` dan `app.include_router(pengguna.router, prefix="/api/v1")`.
    4. Syarat "hanya pengelola" adalah kebijakan penempatan, bukan sifat router. Dengan memasangnya di `include_router`, `admin.py` tetap dapat dipakai ulang di proyek lain dengan syarat berbeda, dan semua kebijakan akses terlihat di satu tempat (`main.py`).

## Ringkasan

- Pecah aplikasi berdasarkan tanggung jawab: satu `APIRouter` per berkas, satu `main.py` yang memasangnya.
- Folder dengan `__init__.py` adalah paket; impor antar berkas memakai impor relatif (`.` dan `..`).
- `prefix` dan `tags` pada `APIRouter` mengatur path dan pengelompokan; `prefix` pada `include_router` ditambahkan di depannya.
- `dependencies` bisa dipasang pada `APIRouter` atau pada `include_router`.
- Taruh kode bersama (dependency, skema) di berkas terpisah untuk menghindari impor melingkar.
- Jalankan paket dengan `fastapi dev app/main.py`, bukan `python app/main.py`.

## Langkah berikutnya

Lanjut ke [Konfigurasi dan Environment](konfigurasi-environment.md), atau kembali ke daftar materi di [Modul 08: Struktur Proyek](index.md).
