# Status Code

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Memilih status code yang tepat untuk situasi umum di API.
- [ ] Mengatur status code sukses dengan `status_code`, termasuk memakai konstanta `status`.
- [ ] Menjelaskan mengapa `204` tidak punya isi.
- [ ] Mengenali status code yang dihasilkan FastAPI secara otomatis: `404`, `405`, `422`, dan `500`.
- [ ] Menggunakan status code untuk memutuskan apakah masalahnya ada di klien atau di server.

## Prasyarat

- Sudah membaca [HTTP dan REST](../01-pengenalan/http-dan-rest.md). Halaman itu memperkenalkan kelompok `2xx` sampai `5xx`; halaman ini membahas cara memilih dan mengaturnya.
- Selesai [Modul 03: Data dan Validasi](../03-data-validasi/index.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7** dan **FastAPI 0.162.0** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

**Status code** adalah angka tiga digit di baris pertama response yang memberi tahu klien hasil request. Klien (aplikasi web, aplikasi ponsel, skrip) sering memutuskan langkah berikutnya hanya dari angka ini, sebelum membaca isinya. Karena itu, memilih status code yang tepat adalah bagian dari merancang API yang baik.

### Memilih status code

Daftar berikut adalah pilihan yang paling sering dipakai. Artinya mengikuti makna umum HTTP (lihat [dokumentasi MDN tentang status code](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)).

| Kode | Nama | Pakai ketika |
|---|---|---|
| `200` | OK | Request berhasil dan ada isi untuk dikembalikan. Ini nilai bawaan. |
| `201` | Created | Data baru berhasil dibuat. |
| `202` | Accepted | Request diterima, tetapi pemrosesannya belum selesai. |
| `204` | No Content | Berhasil, dan memang tidak ada isi untuk dikembalikan (misalnya setelah menghapus). |
| `400` | Bad Request | Request salah dengan cara umum yang tidak punya kode khusus. |
| `401` | Unauthorized | Klien belum membuktikan identitasnya. |
| `403` | Forbidden | Identitas jelas, tetapi tidak punya izin. |
| `404` | Not Found | Data atau path yang diminta tidak ada. |
| `409` | Conflict | Request bertabrakan dengan keadaan data, misalnya nilai unik yang sudah dipakai. |
| `422` | Unprocessable Content | Isi request lengkap secara bentuk tetapi tidak lolos validasi. FastAPI memakainya untuk error validasi. |
| `500` | Internal Server Error | Ada kesalahan tak terduga di kode server. |

Halaman ini mendemonstrasikan `200`, `201`, `202`, `204`, `404`, `405`, `422`, dan `500`. Kode `400`, `401`, `403`, dan `409` hanya dijelaskan: cara mengembalikannya dibahas di halaman berikutnya (`HTTPException`), dan autentikasi di Modul 07.

!!! tip "Cara cepat memutuskan"
    Tanyakan dulu: siapa yang keliru? Kalau permintaan klien yang salah atau tidak diizinkan, pakai `4xx`. Kalau server yang gagal, pakai `5xx`. Jangan menjawab `200` untuk kegagalan hanya karena server "berhasil menjawab".

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/04-penanganan-error/status-code/main.py"
```

## Penjelasan kode

### Impor

```python
from http import HTTPStatus

from fastapi import FastAPI, status
```

`status` dari FastAPI berisi konstanta seperti `status.HTTP_201_CREATED`. `HTTPStatus` adalah enumerasi bawaan Python dengan isi serupa. Menurut dokumentasi FastAPI, parameter `status_code` menerima angka maupun `IntEnum` seperti `HTTPStatus`.

### Status code sukses di dekorator

```python
@app.post("/catatan", status_code=status.HTTP_201_CREATED)
def buat_catatan(isi: str):
```

`status_code` adalah parameter **dekorator**, bukan parameter fungsi. Tanpa parameter ini, jawabannya `200`. Konstanta lebih mudah dibaca daripada angka `201`, dan editor dapat melengkapinya otomatis. Angka biasa (`status_code=201`) hasilnya sama.

### `204` tanpa isi

```python
@app.delete("/catatan/{nomor}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_catatan(nomor: int):
    catatan_db.pop(nomor, None)
```

`204` berarti "berhasil, tidak ada isi". Fungsinya tidak mengembalikan apa pun. `catatan_db.pop(nomor, None)` menghapus data bila ada dan tidak error bila tidak ada.

### Memakai `HTTPStatus`

```python
@app.post("/antrean", status_code=HTTPStatus.ACCEPTED)
```

Hasilnya sama dengan `202`. Pakai salah satu gaya, `status` atau `HTTPStatus`, secara konsisten dalam satu proyek.

### Endpoint yang sengaja rusak

```python
@app.get("/rusak")
def endpoint_rusak():
    return 1 / 0
```

Pembagian dengan nol memicu `ZeroDivisionError`. Kita tidak menangkapnya, sehingga FastAPI menjawab `500`. Endpoint ini hanya untuk mendemonstrasikan `5xx`.

## Menjalankan

```powershell
fastapi dev main.py
```

Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah.

## Mencoba request

Contoh memakai `curl.exe` di PowerShell. Opsi `-i` menampilkan baris status, dan `-X` memilih method.

### Sukses: `200`, `201`, `202`, `204`

```powershell
curl.exe -i http://127.0.0.1:8000/catatan
```

```text
HTTP/1.1 200 OK
{"1":"Belajar status code"}
```

```powershell
curl.exe -i -X POST "http://127.0.0.1:8000/catatan?isi=Catatan%20baru"
```

```text
HTTP/1.1 201 Created
{"nomor":2,"isi":"Catatan baru"}
```

```powershell
curl.exe -i -X POST "http://127.0.0.1:8000/antrean?isi=laporan"
```

```text
HTTP/1.1 202 Accepted
{"pesan":"Diterima, akan diproses nanti","isi":"laporan"}
```

```powershell
curl.exe -i -X DELETE http://127.0.0.1:8000/catatan/1
```

```text
HTTP/1.1 204 No Content
```

Setelah baris header tidak ada isi sama sekali.

### Dihasilkan otomatis oleh FastAPI

| Request | Status | Isi | Penyebab |
|---|---|---|---|
| `GET /tidak-ada` | `404 Not Found` | `{"detail":"Not Found"}` | Path tidak terdaftar |
| `PUT /catatan` | `405 Method Not Allowed` | `{"detail":"Method Not Allowed"}` | Path ada, tetapi method-nya tidak didukung |
| `POST /catatan` (tanpa `isi`) | `422 Unprocessable Content` | `{"detail":[{"type":"missing","loc":["query","isi"],"msg":"Field required","input":null}]}` | Parameter wajib hilang |
| `DELETE /catatan/abc` | `422 Unprocessable Content` | `{"detail":[{"type":"int_parsing","loc":["path","nomor"],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"abc"}]}` | Tipe salah |
| `GET /rusak` | `500 Internal Server Error` | `Internal Server Error` | Exception tak tertangani |

Untuk `/rusak`, terminal server mencatat `ZeroDivisionError: division by zero`. Klien tidak melihat detail itu, hanya `500`. Ini sengaja, supaya rincian internal tidak bocor.

### Status code dan dokumentasi otomatis

`/openapi.json` mencatat status sukses sesuai deklarasi dan menambah `422` untuk endpoint yang punya parameter:

| Endpoint | Status yang tercatat |
|---|---|
| `POST /catatan` | `201`, `422` |
| `DELETE /catatan/{nomor}` | `204`, `422` |
| `POST /antrean` | `202`, `422` |

Tampilan Swagger UI **belum diverifikasi** lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Menaruh `status_code` pada fungsi, bukan dekorator | Parameter ini milik dekorator (`@app.post(...)`). |
| Mengembalikan isi dari endpoint `204` | Diuji dengan `TestClient`: untuk `status_code=204` yang mengembalikan `{"dihapus": 1}`, response tetap `204` dengan isi kosong. Nilai kembalian terbuang. |
| Menjawab `200` untuk kegagalan | Klien tidak bisa membedakan berhasil dan gagal tanpa membaca isi. |
| Mengira `405` sama dengan `404` | `405` berarti path ada, tetapi method salah. Diuji: `GET /catatan/1` menghasilkan `405` karena path itu hanya mendefinisikan `DELETE`. |
| Mengira `500` selalu kesalahan klien | `5xx` selalu masalah di server. Periksa log server. |
| Menghapus data yang tidak ada dan tetap `204` | Pada contoh ini `DELETE /catatan/999` menghasilkan `204`. Bagus atau tidak tergantung rancangan API; menjawab `404` dibahas di halaman berikutnya. |

## Latihan

1. **Pilih kode.** Tentukan status code untuk: (a) membuat akun baru, (b) menghapus akun berhasil, (c) akun tidak ditemukan, (d) email sudah terdaftar, (e) server kehabisan memori.
2. **Praktik.** Buat `POST /pesan` yang menjawab `202` memakai `status.HTTP_202_ACCEPTED`. Apa isi `responses` di `/openapi.json`?
3. **Prediksi.** Pada `main.py`, apa status untuk `GET /catatan/1`, `DELETE /catatan`, dan `POST /antrean?isi=x`?
4. **Analisis.** Mengapa FastAPI menjawab `422`, bukan `400`, untuk `DELETE /catatan/abc`, dan mengapa `500` tidak menampilkan pesan `ZeroDivisionError` ke klien?

??? success "Kunci jawaban"
    1. Jawaban 1(a) sampai 1(c) dan 1(e) mengikuti tabel di atas, 1(d) mengikuti makna umum HTTP; semuanya adalah penalaran, tidak dijalankan.
        - (a) `201`.
        - (b) `204`.
        - (c) `404`.
        - (d) `409`.
        - (e) `500`.
    2. Diuji dengan `TestClient`:

        ```python
        from fastapi import FastAPI, status

        app = FastAPI()


        @app.post("/pesan", status_code=status.HTTP_202_ACCEPTED)
        def pesan():
            return {"ok": True}
        ```

        Request menghasilkan `202`, dan `responses` berisi `['202']` saja (tanpa `422` karena endpoint ini tidak punya parameter).
    3. Diuji: `GET /catatan/1` adalah `405`, `DELETE /catatan` adalah `405` (path ada tetapi method tidak terdaftar), dan `POST /antrean?isi=x` adalah `202`.
    4. `422` dipakai FastAPI khusus untuk data yang tidak lolos validasi (teruji: error `int_parsing`). Alasan `500` tidak menampilkan detail: itu rincian internal, jadi klien hanya menerima `Internal Server Error` sedangkan log server memuat detailnya (teruji untuk log). Bagian "mengapa memilih `422` bukan `400`" adalah keputusan desain FastAPI; halaman ini tidak menelusuri alasannya.

## Ringkasan

- Status code menyatakan hasil request; pilih berdasarkan siapa yang keliru: klien (`4xx`) atau server (`5xx`).
- Atur status sukses dengan `status_code` pada dekorator; konstanta `status` atau `HTTPStatus` membuat kode mudah dibaca.
- `201` untuk data baru, `202` untuk diterima tetapi belum diproses, `204` untuk sukses tanpa isi.
- FastAPI menjawab otomatis `404` (path tidak ada), `405` (method salah), `422` (validasi gagal), dan `500` (exception tak tertangani).
- `204` tidak membawa isi, walau fungsi mengembalikan sesuatu.

## Langkah berikutnya

Kembali ke daftar materi di [Modul 04: Penanganan Error](index.md). Materi berikutnya adalah `HTTPException`, yaitu cara mengembalikan `404`, `409`, dan error lain dari kode kita sendiri.
