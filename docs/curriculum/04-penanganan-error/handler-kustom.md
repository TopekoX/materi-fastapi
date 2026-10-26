# Handler Error Kustom

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan apa itu exception handler dan kapan ia dijalankan.
- [ ] Membuat exception sendiri dan handler-nya dengan `@app.exception_handler`.
- [ ] Mengganti bentuk response `HTTPException` dan error validasi (`RequestValidationError`).
- [ ] Menyeragamkan semua error API ke satu format.
- [ ] Menyembunyikan detail internal dari error `500`.
- [ ] Membungkus handler bawaan FastAPI, misalnya untuk menambah pencatatan.

## Prasyarat

- Sudah membaca [HTTPException](http-exception.md) dan [Error Validasi](error-validasi.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, dan **Pydantic 2.14.1** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Sejauh ini bentuk error kita tidak seragam:

- error buatan kita: `{"detail": "teks"}` atau `{"detail": {...}}`,
- error validasi: `{"detail": [ ... ]}`,
- `404` untuk path tak dikenal: `{"detail": "Not Found"}`,
- `500`: teks polos `Internal Server Error`.

Klien harus menangani semua bentuk itu. **Exception handler** memecahkan masalah ini. Handler adalah fungsi yang dijalankan FastAPI ketika sebuah jenis exception terjadi, dan fungsi itu menentukan response yang dikirim.

Kita akan membuat satu format error untuk seluruh API:

```json
{"galat": {"kode": "...", "pesan": "...", "rincian": []}}
```

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/04-penanganan-error/handler-kustom/main.py"
```

## Penjelasan kode

### Impor

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
```

- `Request` adalah objek request yang diterima handler.
- `RequestValidationError` adalah exception yang dibuat FastAPI saat validasi gagal.
- `JSONResponse` membuat response JSON dengan status yang kita tentukan.
- `StarletteHTTPException` adalah kelas induk `HTTPException` FastAPI. Menurut dokumentasi FastAPI, handler didaftarkan untuk kelas Starlette ini agar juga menangkap error yang dilempar Starlette sendiri, misalnya `404` untuk path tak dikenal.

### Exception sendiri

```python
class BukuTidakDitemukan(Exception):
    def __init__(self, buku_id: int):
        self.buku_id = buku_id
```

Exception biasa Python yang membawa `buku_id`. Dengan exception sendiri, kode endpoint cukup menyatakan **apa yang terjadi** (`raise BukuTidakDitemukan(id)`), sedangkan **bagaimana dijawab** diatur di satu tempat: handler.

### Fungsi pembentuk response

```python
def respons_galat(status_code, kode, pesan, rincian=None):
    isi = {"galat": {"kode": kode, "pesan": pesan, "rincian": rincian or []}}
    return JSONResponse(status_code=status_code, content=isi)
```

Semua handler memakai fungsi ini, sehingga bentuk error pasti sama.

### Handler untuk exception sendiri

```python
@app.exception_handler(BukuTidakDitemukan)
async def buku_tidak_ditemukan_handler(request: Request, exc: BukuTidakDitemukan):
    return respons_galat(404, "BUKU_TIDAK_ADA", f"Buku dengan id {exc.buku_id} tidak ditemukan")
```

`@app.exception_handler(Kelas)` mendaftarkan fungsi sebagai handler untuk `Kelas`. Handler menerima `request` dan exception-nya (`exc`), lalu mengembalikan response.

### Handler `HTTPException`

```python
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return respons_galat(exc.status_code, f"HTTP_{exc.status_code}", str(exc.detail))
```

Semua `HTTPException` (termasuk `404` dan `405` otomatis) kini memakai format kita. `str(exc.detail)` mengubah `detail` menjadi teks.

### Handler error validasi

```python
@app.exception_handler(RequestValidationError)
async def validasi_handler(request: Request, exc: RequestValidationError):
    rincian = [
        {"field": ".".join(str(b) for b in galat["loc"]), "jenis": galat["type"], "pesan": galat["msg"]}
        for galat in exc.errors()
    ]
    return respons_galat(422, "VALIDASI_GAGAL", "Data yang dikirim tidak valid", rincian)
```

`exc.errors()` mengembalikan daftar error yang sama seperti `detail` bawaan. Kita memilih hanya `loc`, `type`, dan `msg`, lalu menggabungkan `loc` menjadi teks seperti `body.judul`. Dokumentasi FastAPI mengingatkan agar tidak mengubah seluruh exception menjadi teks karena dapat memuat informasi sistem; mengambil bagian yang kita butuhkan lebih aman.

### Handler untuk semua exception lain

```python
@app.exception_handler(Exception)
async def galat_tak_terduga_handler(request: Request, exc: Exception):
    return respons_galat(500, "GALAT_SERVER", "Terjadi kesalahan pada server")
```

Handler untuk `Exception` menangkap kesalahan yang tidak diduga. Klien hanya menerima pesan umum. Rincian kesalahan tetap tercatat di log server (lihat hasil uji di bawah).

### Endpoint

Endpoint memakai `raise BukuTidakDitemukan(buku_id)` untuk `404` dan `HTTPException(409, ...)` untuk judul duplikat. Keduanya berakhir di handler yang sesuai. Endpoint `/rusak` sengaja membagi dengan nol untuk memicu `500`.

## Menjalankan

```powershell
fastapi dev main.py
```

Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah.

## Mencoba request

Hasil di bawah dijalankan dengan `curl.exe` ke server `fastapi dev`.

### Semua error berformat sama

| Request | Status | Isi |
|---|---|---|
| `GET /buku/1` | `200` | `{"id":1,"judul":"Dasar Python","tahun":2020}` |
| `GET /buku/99` | `404` | `{"galat":{"kode":"BUKU_TIDAK_ADA","pesan":"Buku dengan id 99 tidak ditemukan","rincian":[]}}` |
| `GET /tidak-ada` | `404` | `{"galat":{"kode":"HTTP_404","pesan":"Not Found","rincian":[]}}` |
| `PUT /buku/1` | `405` | `{"galat":{"kode":"HTTP_405","pesan":"Method Not Allowed","rincian":[]}}` |
| `GET /rusak` | `500` | `{"galat":{"kode":"GALAT_SERVER","pesan":"Terjadi kesalahan pada server","rincian":[]}}` |

Untuk `/rusak`, terminal server tetap mencatat `ZeroDivisionError`. Handler hanya mengubah apa yang dilihat klien; pencatatan di server tidak hilang.

### Error validasi dan `HTTPException` buatan sendiri

Request validasi salah (`GET /buku/abc`):

```json
{"galat":{"kode":"VALIDASI_GAGAL","pesan":"Data yang dikirim tidak valid","rincian":[{"field":"path.buku_id","jenis":"int_parsing","pesan":"Input should be a valid integer, unable to parse string as an integer"}]}}
```

Body `{"judul":"ab","tahun":1800}` ke `POST /buku`:

```json
{"galat":{"kode":"VALIDASI_GAGAL","pesan":"Data yang dikirim tidak valid","rincian":[{"field":"body.judul","jenis":"string_too_short","pesan":"String should have at least 3 characters"},{"field":"body.tahun","jenis":"greater_than_equal","pesan":"Input should be greater than or equal to 1900"}]}}
```

Body `{"judul":"Dasar Python","tahun":2021}` (judul sudah ada) menghasilkan `409`:

```json
{"galat":{"kode":"HTTP_409","pesan":"Judul sudah ada","rincian":[]}}
```

Body `{"judul":"Belajar HTTP","tahun":2021}` menghasilkan `201` dengan `{"id":2,"judul":"Belajar HTTP","tahun":2021}`.

### Membungkus handler bawaan

Handler bawaan bisa dipanggil dari handler kita, misalnya untuk menambah pencatatan. Diuji dengan `TestClient`:

```python
from fastapi.exception_handlers import request_validation_exception_handler

@app.exception_handler(RequestValidationError)
async def handler(request, exc):
    print("LOG:", len(exc.errors()), "error")
    return await request_validation_exception_handler(request, exc)
```

Hasilnya: baris `LOG: 1 error` tercetak, dan response tetap berbentuk bawaan (`422` dengan `{"detail":[...]}`). Dokumentasi FastAPI memuat pola yang sama untuk `http_exception_handler`.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Mendaftarkan handler untuk `HTTPException` FastAPI, bukan Starlette | Error yang dilempar Starlette sendiri (misalnya `404` path tak dikenal) tidak tertangkap. Daftarkan untuk `StarletteHTTPException` (dokumentasi FastAPI). |
| Memakai `str(exc.detail)` untuk `detail` berupa objek | Teruji: `detail={"kode": "X", "pesan": "p"}` menjadi `"pesan": "{'kode': 'X', 'pesan': 'p'}"`, yaitu teks, bukan JSON. Olah dulu bila `detail` bisa berupa objek. |
| Menampilkan `str(exc)` pada `500` | Rincian internal bisa bocor ke klien. Kirim pesan umum, catat rincian di log. |
| Mengubah seluruh `RequestValidationError` menjadi teks | Dokumentasi menyatakan ia dapat memuat informasi sistem. Ambil bagian `loc`, `type`, `msg` saja. |
| Lupa bahwa status `422` tetap perlu ditentukan | Handler yang mengembalikan response tanpa `status_code` menjawab `200`. Selalu tentukan status. |
| Menaruh logika bisnis di handler | Handler hanya menerjemahkan exception menjadi response. |

## Latihan

1. **Exception baru.** Buat `StokHabis(nama)` dan handler yang menjawab `409` dengan kode `STOK_HABIS`. Endpoint `GET /beli/{nama}` me-raise-nya bila `nama == "pensil"`.
2. **Tangani `detail` objek.** Pada `http_exception_handler`, bagaimana agar `detail` berupa `dict` ikut tampil sebagai JSON di `rincian`, bukan teks?
3. **Prediksi.** Apa yang dilihat klien dan apa yang tercatat di log untuk `GET /rusak`?
4. **Analisis.** Mengapa kode endpoint tidak perlu tahu bentuk JSON error?

??? success "Kunci jawaban"
    Jawaban 1 dijalankan dengan `TestClient`. Jawaban 2 adalah rancangan yang tidak dijalankan. Jawaban 3 dari hasil `curl` dan log server.

    ```python
    class StokHabis(Exception):
        def __init__(self, nama: str):
            self.nama = nama


    @app.exception_handler(StokHabis)
    async def stok_habis_handler(request: Request, exc: StokHabis):
        return respons_galat(409, "STOK_HABIS", f"Stok {exc.nama} habis")


    @app.get("/beli/{nama}")
    def beli(nama: str):
        if nama == "pensil":
            raise StokHabis(nama)
        return {"nama": nama}
    ```

    1. `/beli/pensil` menghasilkan `409` dengan `{"galat":{"kode":"STOK_HABIS","pesan":"Stok pensil habis","rincian":[]}}`. `/beli/buku` menghasilkan `200`.
    2. Periksa `isinstance(exc.detail, (dict, list))`; bila ya, kirim lewat argumen `rincian` (misalnya `[exc.detail]`) alih-alih `str(...)`. Ini rancangan, belum dijalankan.
    3. Klien melihat `500` dengan pesan umum `Terjadi kesalahan pada server`; log server mencatat `ZeroDivisionError`.
    4. Endpoint hanya menyatakan kejadian (`raise ...`), sedangkan bentuk response diurus handler. Mengubah format error cukup di handler, tanpa menyentuh endpoint.

## Ringkasan

- Exception handler adalah fungsi yang menentukan response untuk jenis exception tertentu.
- Daftarkan dengan `@app.exception_handler(KelasException)`; handler menerima `request` dan `exc`.
- Untuk `HTTPException`, daftarkan `StarletteHTTPException` agar semua error HTTP tertangkap.
- Untuk error validasi, tangani `RequestValidationError` dan ambil `exc.errors()`.
- Handler untuk `Exception` menyembunyikan detail `500` dari klien; log server tetap mencatatnya.
- Dengan satu fungsi pembentuk response, seluruh error API berformat sama.
- Handler bawaan dapat dibungkus untuk menambah pencatatan.

## Langkah berikutnya

Kembali ke daftar materi di [Modul 04: Penanganan Error](index.md). Materi berikutnya adalah proyek praktik tahap 2, yaitu menerapkan semua ini pada TugasKu API.
