# Aplikasi Pertama

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Membedakan *aplikasi* FastAPI dari *endpoint* dan dari *server*.
- [ ] Membuat objek aplikasi lengkap dengan judul, deskripsi, dan versi.
- [ ] Menjelaskan arti `main:app` dan bagaimana server menemukan aplikasimu.
- [ ] Menjalankan aplikasi dengan `fastapi dev` dan dengan `uvicorn`.
- [ ] Mengenali kesalahan umum saat aplikasi tidak mau berjalan.

## Prasyarat

- Sudah membaca [Apa itu FastAPI](apa-itu-fastapi.md).
- Sudah menyiapkan environment sesuai [Instalasi dan Virtual Environment](instalasi-dan-venv.md), dengan venv aktif dan FastAPI terpasang.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7** dan **FastAPI 0.162.0** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep: aplikasi, endpoint, dan server

Tiga istilah ini sering tertukar. Bedanya:

| Istilah | Apa itu | Di mana |
|---|---|---|
| **Aplikasi** | Objek `FastAPI` yang menampung semua endpoint beserta pengaturannya | Di kodemu |
| **Endpoint** | Satu pasangan path dan HTTP method yang dilayani aplikasi | Di kodemu, didaftarkan ke aplikasi |
| **Server** | Program yang menerima koneksi dari klien lalu meneruskannya ke aplikasi | Program terpisah, misalnya Uvicorn |

Cara membuat endpoint sudah dibahas di [Endpoint Pertama](endpoint-pertama.md). Halaman ini berfokus pada aplikasinya.

Ada satu hal penting: **aplikasi tidak menjalankan dirinya sendiri**. Objek `FastAPI` hanya berisi aturan, yaitu "jika ada request ini, panggil fungsi itu". Agar ada yang mendengarkan request, kamu perlu server yang diberi tahu di mana aplikasimu berada.

## Kode lengkap

Simpan sebagai `main.py` di folder kerja:

```python title="main.py"
--8<-- "fastapi/01-pengenalan/aplikasi-pertama/main.py"
```

## Penjelasan kode

### Membuat aplikasi dengan metadata

```python
app = FastAPI(
    title="Belajar FastAPI",
    description="Aplikasi pertama dari materi Belajar FastAPI.",
    version="0.1.0",
)
```

Pada [Endpoint Pertama](endpoint-pertama.md), `FastAPI()` dipanggil tanpa isian. Di sini ada tiga parameter:

| Parameter | Fungsinya |
|---|---|
| `title` | Nama API. Tampil sebagai judul di dokumentasi interaktif |
| `description` | Penjelasan singkat tentang API |
| `version` | Nomor versi **API-mu sendiri**, bukan versi FastAPI |

Ketiganya dimasukkan ke deskripsi OpenAPI yang dibuat otomatis. Pada pengujian, bagian `info` di `/openapi.json` berisi tepat nilai-nilai ini (lihat bagian hasil di bawah).

### Dua endpoint

```python
@app.get("/")
def halaman_utama():
    return {"pesan": "Aplikasi pertama berjalan!"}


@app.get("/kesehatan")
def kesehatan():
    return {"status": "ok"}
```

Endpoint pertama menyapa pengguna. Endpoint kedua, `/kesehatan`, adalah kebiasaan umum: sebuah endpoint kecil yang hanya menjawab "aplikasi hidup". Nama `/kesehatan` bukan fitur bawaan FastAPI; kamu bebas memilih nama lain.

### Hubungan antarbagian

```text
main.py
 └─ app = FastAPI(...)          ← aplikasi (objek)
      ├─ @app.get("/")          ← endpoint 1
      └─ @app.get("/kesehatan") ← endpoint 2

Server  →  "muat objek app dari main.py"  →  melayani request
```

## Bagaimana server menemukan aplikasi?

Server perlu dua informasi: **file** mana dan **variabel** mana. Keduanya ditulis dalam bentuk `file:variabel`, disebut *import string*. Untuk kodemu:

```text
main:app
 │    └─ nama variabel yang menyimpan objek FastAPI
 └────── nama file tanpa ekstensi .py
```

Pada pengujian, perintah `fastapi dev main.py` mencetak `Using import string: main:app`, jadi bentuk inilah yang dipakai di balik layar.

## Menjalankan aplikasi

Pastikan venv aktif dan terminal berada di folder `main.py`.

### Cara 1: `fastapi dev`

```bash
fastapi dev main.py
```

Ini cara yang dipakai di materi ini. Log pada pengujian menampilkan (cuplikan):

```text
Using import string: main:app
Server started at http://127.0.0.1:8768
Will watch for changes in these directories: [...]
Application startup complete.
```

Nomor port pada komputermu biasanya `8000`. Pada pengujian dipakai `8768` agar tidak bentrok. Ubah port dengan `--port` bila perlu.

### Cara 2: `uvicorn`

```bash
python -m uvicorn main:app --port 8000
```

Di sini kamu menyebut import string sendiri. `python -m uvicorn` menjalankan Uvicorn dari environment yang sedang aktif. Pada pengujian, perintah ini melayani aplikasi dengan hasil yang sama persis.

Perintah `fastapi dev` menambahkan kemudahan untuk pengembangan, termasuk pemantauan perubahan file. Opsi `--reload` pada `uvicorn` untuk keperluan serupa **tidak saya uji**.

## Mencoba aplikasi

Gunakan terminal kedua (pengguna PowerShell: ketik `curl.exe`):

```bash
curl -i http://127.0.0.1:8000/
curl -i http://127.0.0.1:8000/kesehatan
```

Hasil dari eksekusi nyata:

| Request | Status | Body |
|---|---|---|
| `GET /` | `200 OK` | `{"pesan":"Aplikasi pertama berjalan!"}` |
| `GET /kesehatan` | `200 OK` | `{"status":"ok"}` |

### Metadata di dokumentasi

Bagian `info` pada `http://127.0.0.1:8000/openapi.json` berisi (hasil nyata):

```python
{'title': 'Belajar FastAPI',
 'description': 'Aplikasi pertama dari materi Belajar FastAPI.',
 'version': '0.1.0'}
```

Judul halaman `/docs` pada pengujian adalah `Belajar FastAPI - Swagger UI`, yaitu `title` yang kamu tulis. Di berkas yang sama juga ada bidang `openapi` bernilai `3.1.0`. Itu versi standar OpenAPI, tidak berhubungan dengan `version="0.1.0"` milikmu.

!!! warning "Belum diverifikasi secara visual"
    Tampilan Swagger UI di browser belum saya lihat langsung, dan halamannya butuh internet karena memuat berkas dari CDN.

### Mengubah kode saat server berjalan

Log `fastapi dev` menyatakan server memantau perubahan file. Pada pengujian, setelah `main.py` diubah, log memang mencatat `WatchFiles detected changes in 'main.py'. Reloading...`. Namun di lingkungan uji saya (proses tanpa terminal interaktif), server **tidak benar-benar restart**: respons tetap versi lama selama 17 detik. Jadi saya tidak dapat memastikan perilaku reload di terminalmu. Jika perubahanmu tidak tampil, hentikan server dengan `Ctrl+C` lalu jalankan ulang.

## Kesalahan umum

Semua kasus berikut dijalankan dan dicatat apa adanya.

### 1. Menjalankan `python main.py` dan tidak terjadi apa-apa

```bash
python main.py
```

Perintah selesai tanpa error dan tanpa output, dan tidak ada server yang berjalan. Python hanya membaca file dan membuat objek `app`, lalu selesai. **Solusi:** jalankan lewat server, yaitu `fastapi dev main.py` atau `uvicorn`.

### 2. Nama variabel pada `uvicorn` salah

```bash
python -m uvicorn main:salah
```

Hasilnya:

```text
ERROR:    Error loading ASGI app. Attribute "salah" not found in module "main".
```

**Solusi:** pastikan bagian setelah titik dua sama dengan nama variabel di kodemu. Pada `main:app`, variabelnya harus bernama `app`.

### 3. Mengira variabel harus bernama `app`

Tidak selalu. Ketika variabel diganti menjadi `aplikasi`, `fastapi dev` tetap berhasil karena menemukan objek `FastAPI` sendiri (log menampilkan `Using import string: <nama file>:aplikasi`). Sedangkan `uvicorn` selalu butuh nama yang tepat, misalnya `modul_lain:aplikasi` untuk file `modul_lain.py` (berhasil pada pengujian). Pakai `app` agar sesuai kebiasaan dan dokumentasi.

### 4. Folder atau nama file keliru

Jika nama file salah, `fastapi dev salah.py` menghasilkan `Path does not exist salah.py` (lihat [Endpoint Pertama](endpoint-pertama.md#kesalahan-umum)). **Solusi:** periksa nama file dan folder kerja terminal.

## Latihan

1. **Dasar.** Ubah `title`, `description`, dan `version` menjadi milikmu sendiri. Jalankan ulang, lalu buka `/openapi.json` dan periksa bagian `info`.
2. **Menengah.** Jalankan aplikasi dengan `python -m uvicorn main:app`, lalu panggil `/kesehatan` dengan `curl -i`.
3. **Menengah.** Tambahkan endpoint `GET /versi` yang mengembalikan versi API-mu dalam bentuk `{"versi": "..."}`. Petunjuk: objek `app` menyimpan versi di atribut `version`.
4. **Tantangan.** Ganti nama variabel `app` menjadi `aplikasi` (di pembuatan objek dan di semua decorator). Jalankan dengan `uvicorn`, lalu tentukan import string yang benar.

??? success "Petunjuk jawaban"
    1. Bagian `info` berisi nilai barumu. Pada pengujian dengan `title="Judul Baru"`, `description="Deskripsi baru."`, `version="1.2.3"`, `info` menampilkan ketiganya.
    2. Hasil sama dengan `fastapi dev`: `200 OK` dan `{"status":"ok"}` (teramati pada pengujian).
    3. Kode:

        ```python
        @app.get("/versi")
        def versi():
            return {"versi": app.version}
        ```

        Dengan `version="1.2.3"`, hasilnya `{"versi":"1.2.3"}`. Jawaban ini diuji dengan `TestClient` dari FastAPI, bukan lewat `curl`.
    4. Import string-nya `main:aplikasi`. Pada pengujian, bentuk `modul_lain:aplikasi` (file bernama `modul_lain.py`) melayani `GET /` dengan `200 OK`.

## Ringkasan

- **Aplikasi** adalah objek `FastAPI` yang menampung endpoint dan pengaturan. **Server** adalah program terpisah yang melayani request.
- Aplikasi tidak berjalan sendiri: `python main.py` tidak menyalakan server.
- `title`, `description`, dan `version` pada `FastAPI(...)` muncul di dokumentasi otomatis. `version` adalah versi API-mu.
- Server menemukan aplikasi lewat import string `file:variabel`, misalnya `main:app`.
- `fastapi dev main.py` dan `python -m uvicorn main:app` sama-sama dapat melayani aplikasi ini.
- Perilaku reload otomatis belum bisa saya pastikan; bila perubahan tidak tampil, restart manual.

## Langkah berikutnya

Lanjutkan ke [Endpoint Pertama](endpoint-pertama.md) untuk membahas endpoint lebih dalam, atau kembali ke [Modul 01: Pengenalan](index.md).
