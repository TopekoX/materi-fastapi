# Endpoint Pertama

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan apa itu *endpoint*, *path*, dan *HTTP method*.
- [ ] Menulis aplikasi FastAPI dengan dua endpoint.
- [ ] Menjalankan aplikasi dan memanggil endpoint-nya dengan browser dan `curl`.
- [ ] Membaca response, termasuk status code dan isi JSON-nya.
- [ ] Mengenali dan memperbaiki kesalahan umum pada endpoint pertama.

## Prasyarat

- Sudah membaca [Apa itu FastAPI](apa-itu-fastapi.md).
- Python terpasang dan kamu bisa memakai terminal.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7** dan **FastAPI 0.162.0** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain atau sistem operasi lain **belum diuji**.

## Konsep: endpoint

Pada halaman sebelumnya kamu sudah mengenal klien yang mengirim *request* dan server yang membalas dengan *response*. Agar server tahu apa yang diminta, setiap request membawa dua informasi:

| Informasi | Artinya | Contoh |
|---|---|---|
| **Path** | Alamat sumber daya yang diminta, yaitu bagian URL setelah nama server | `/` atau `/tentang` |
| **HTTP method** | Jenis tindakan yang diminta | `GET` untuk mengambil data |

Pasangan *path + method* disebut **endpoint**. Satu endpoint punya satu tugas, misalnya "ambil informasi tentang aplikasi".

Di FastAPI, kamu membuat endpoint dengan menulis sebuah fungsi Python biasa, lalu "menempelkannya" pada path dan method tertentu. Dokumentasi resmi menyebut fungsi ini *path operation function*. Fungsi itu hanya perlu mengembalikan data. FastAPI yang mengubahnya menjadi response JSON.

## Persiapan

Buat folder kerja, lalu siapkan *virtual environment* agar paket yang kamu pasang tidak bercampur dengan proyek lain. Versi ringkas ada di bawah; penjelasan lengkap, termasuk cara memverifikasi dan menyimpan dependensi, ada di [Instalasi dan Virtual Environment](instalasi-dan-venv.md).

=== "Windows (PowerShell)"

    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install "fastapi[standard]"
    ```

=== "macOS / Linux"

    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install "fastapi[standard]"
    ```

!!! note "Yang dipasang"
    `fastapi[standard]` memasang FastAPI beserta paket pendukung, termasuk perintah `fastapi` dan Uvicorn. Pada pengujian ini keduanya terpasang bersama FastAPI. Tab macOS/Linux **belum diuji**.

Untuk mendapatkan versi yang sama dengan halaman ini, pakai `pip install "fastapi[standard]==0.162.0"`.

## Kode lengkap

Simpan kode berikut sebagai `main.py` di folder kerja:

```python title="main.py"
--8<-- "fastapi/01-pengenalan/endpoint-pertama/main.py"
```

## Penjelasan kode

### Mengimpor FastAPI

```python
from fastapi import FastAPI
```

Baris ini mengambil kelas `FastAPI` dari paket `fastapi`. Kelas inilah yang menjadi inti aplikasimu.

### Membuat aplikasi

```python
app = FastAPI()
```

Baris ini membuat satu objek aplikasi dan menyimpannya di variabel `app`. Semua endpoint akan didaftarkan ke objek ini. Nama `app` adalah kebiasaan yang dipakai pada contoh resmi. Perintah `fastapi dev` dapat menemukan objek ini sendiri, tetapi `uvicorn` perlu diberi nama variabel yang tepat; penjelasannya ada di [Aplikasi Pertama](aplikasi-pertama.md#bagaimana-server-menemukan-aplikasi).

### Mendaftarkan endpoint

```python
@app.get("/")
def halaman_utama():
    return {"pesan": "Halo, FastAPI!"}
```

Bagian ini terdiri dari tiga unsur:

| Unsur | Fungsinya |
|---|---|
| `@app.get("/")` | *Decorator*. Memberi tahu FastAPI: "fungsi di bawah ini menangani request ber-method `GET` ke path `/`". Kata `get` menentukan HTTP method, dan `"/"` menentukan path |
| `def halaman_utama():` | Fungsi yang dipanggil FastAPI setiap kali ada request yang cocok. Nama fungsi bebas, tidak harus sama dengan path |
| `return {...}` | Nilai yang dikembalikan. `dict` Python diubah otomatis menjadi JSON |

Path `/` adalah alamat paling dasar, yaitu halaman utama server.

### Endpoint kedua

```python
@app.get("/tentang")
def tentang():
    return {"nama": "Belajar FastAPI", "modul": 1}
```

Polanya sama, hanya path dan isi yang berbeda. Perhatikan bahwa path ditulis dengan garis miring di depan (`"/tentang"`). Jika terlupa, endpoint tidak ditemukan; lihat bagian [kesalahan umum](#kesalahan-umum).

### Hubungan antarbagian

```text
@app.get("/tentang")   →   path "/tentang" + method GET
        │
        ▼
def tentang(): ...     →   dipanggil saat ada request itu
        │
        ▼
return {...}           →   diubah FastAPI menjadi response JSON
```

!!! note "`def` atau `async def`"
    Dokumentasi resmi memakai `async def` pada contoh pertamanya dan menyebut bahwa `def` biasa juga bisa dipakai. Halaman ini memakai `def` agar fokus ke konsep endpoint. Perbedaannya dibahas di [Dasar Async/Await](../02-dasar-routing/async-await.md).

## Menjalankan aplikasi

Pastikan terminal berada di folder yang berisi `main.py` dan *virtual environment* aktif, lalu jalankan:

```bash
fastapi dev main.py
```

| Bagian perintah | Artinya |
|---|---|
| `fastapi dev` | Menjalankan server dalam mode pengembangan |
| `main.py` | File yang berisi aplikasimu |

Output (cuplikan, tidak lengkap):

```text
Server started at http://127.0.0.1:8000
Documentation at http://127.0.0.1:8000/docs
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

Log juga menampilkan `Will watch for changes in these directories`, yang menandakan server memantau perubahan pada file. Biarkan terminal ini tetap terbuka. Untuk berhenti, tekan `Ctrl+C`.

Jika port `8000` sudah dipakai program lain, tambahkan `--port` dengan nomor lain, misalnya `fastapi dev main.py --port 8765`. Opsi ini sudah diuji, dan alamat pada langkah berikut menyesuaikan nomor port tersebut.

## Mencoba endpoint

### Dengan browser

Buka `http://127.0.0.1:8000/` dan `http://127.0.0.1:8000/tentang`. Browser mengirim request `GET`, sehingga cocok untuk endpoint ini.

### Dengan `curl`

Buka terminal kedua (biarkan server tetap berjalan):

```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/tentang
```

!!! warning "Pengguna PowerShell"
    Di Windows PowerShell, `curl` adalah alias untuk perintah lain. Ketik `curl.exe` agar yang terpanggil adalah program `curl`. Perintah di atas diuji dengan `curl`, bukan alias PowerShell.

### Hasil yang diharapkan

Hasil berikut berasal dari eksekusi nyata:

| Request | Status | Isi response |
|---|---|---|
| `GET /` | `200 OK` | `{"pesan":"Halo, FastAPI!"}` |
| `GET /tentang` | `200 OK` | `{"nama":"Belajar FastAPI","modul":1}` |

Kedua response memiliki header `content-type: application/json`. Status `200 OK` berarti request berhasil.

### Dokumentasi interaktif

Buka `http://127.0.0.1:8000/docs`. Di sana ada Swagger UI yang menampilkan kedua endpoint dan memungkinkanmu memanggilnya langsung. Alamat `http://127.0.0.1:8000/redoc` menampilkan tampilan alternatif (ReDoc).

Kamu tidak menulis dokumentasi itu. FastAPI membuatnya dari kodemu dan menyediakan deskripsinya dalam format OpenAPI di `http://127.0.0.1:8000/openapi.json`. Di sana terlihat bahwa judul endpoint diturunkan dari nama fungsi: `halaman_utama` menjadi "Halaman Utama" dan `tentang` menjadi "Tentang". Cara memperkaya dan mengatur dokumentasi ini dibahas di [Dokumentasi Interaktif](dokumentasi-interaktif.md).

!!! warning "Belum diverifikasi secara visual"
    Server terbukti melayani `/docs` dan `/redoc` dengan status `200`, dan halamannya memuat berkas dari `cdn.jsdelivr.net`, sehingga **butuh koneksi internet**. Tampilan Swagger UI di browser belum saya lihat langsung.

## Kesalahan umum

Semua kasus berikut dijalankan dan hasilnya dicatat apa adanya.

### 1. Nama file salah atau folder keliru

```bash
fastapi dev salah.py
```

Hasilnya `Path does not exist salah.py`. **Solusi:** pastikan nama file benar dan terminal berada di folder yang berisi file itu.

### 2. Lupa garis miring di depan path

Jika ditulis `@app.get("tentang")` (tanpa `/`), server tetap menyala tanpa pesan kesalahan, tetapi `GET /tentang` mengembalikan `404 Not Found` dengan isi `{"detail":"Not Found"}`. **Solusi:** tulis path diawali `/`.

### 3. Path yang tidak terdaftar

`GET /tidak-ada` mengembalikan `404 Not Found` dengan isi `{"detail":"Not Found"}`. **Solusi:** periksa ejaan path, dan cek daftar endpoint di `/docs`.

### 4. Method yang salah

Endpoint `/` hanya didaftarkan untuk `GET`. Request `POST /` mengembalikan `405 Method Not Allowed` dengan isi `{"detail":"Method Not Allowed"}`, dan header `allow: GET` menunjukkan method yang diterima. **Solusi:** pakai method yang sesuai dengan decorator.

!!! tip "Membedakan 404 dan 405"
    `404` berarti path-nya tidak ada. `405` berarti path-nya ada, tetapi method yang dipakai tidak didukung.

## Latihan

1. **Dasar.** Tambahkan endpoint `GET /salam` yang mengembalikan `{"pesan": "Selamat belajar!"}`. Simpan file, lalu panggil dengan `curl`.
2. **Menengah.** Tambahkan endpoint `GET /angka` yang mengembalikan bilangan `42`, dan `GET /daftar` yang mengembalikan list `["python", "fastapi"]`. Perhatikan bentuk response-nya.
3. **Tantangan.** Tambahkan endpoint `GET /beda` dengan nama fungsi `nama_fungsi_lain`. Buka `/openapi.json` atau `/docs` dan amati judul yang muncul. Jelaskan hubungan judul itu dengan nama fungsi.

??? success "Kunci jawaban (sudah dijalankan)"
    ```python
    @app.get("/salam")
    def salam():
        return {"pesan": "Selamat belajar!"}


    @app.get("/angka")
    def angka():
        return 42


    @app.get("/daftar")
    def daftar():
        return ["python", "fastapi"]


    @app.get("/beda")
    def nama_fungsi_lain():
        return {"ok": True}
    ```

    Hasil yang teramati, semuanya `200` dengan `content-type: application/json`:

    | Endpoint | Isi response |
    |---|---|
    | `/salam` | `{"pesan":"Selamat belajar!"}` |
    | `/angka` | `42` |
    | `/daftar` | `["python","fastapi"]` |
    | `/beda` | `{"ok":true}` |

    Untuk latihan 3, judul endpoint di dokumentasi menjadi "Nama Fungsi Lain": judul diturunkan dari nama fungsi, bukan dari path.

    Jawaban ini diuji dengan `TestClient` dari FastAPI, bukan lewat browser.

## Ringkasan

- **Endpoint** adalah pasangan *path* dan *HTTP method*.
- Di FastAPI, endpoint dibuat dengan menempelkan decorator seperti `@app.get("/path")` pada sebuah fungsi.
- Nilai yang dikembalikan fungsi, misalnya `dict`, angka, atau list, diubah otomatis menjadi response JSON.
- Aplikasi dijalankan dengan `fastapi dev main.py` dan dicoba lewat browser, `curl`, atau `/docs`.
- `404` berarti path tidak ditemukan, `405` berarti method tidak didukung.
- Dokumentasi interaktif dibuat otomatis dari kodemu.

## Langkah berikutnya

Kembali ke daftar materi di [Modul 01: Pengenalan](index.md), atau lihat seluruh rencana di [Kurikulum](../index.md).
