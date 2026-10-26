# Menjalankan Server

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan arti host dan port pada alamat server.
- [ ] Membedakan `fastapi dev` dan `fastapi run`.
- [ ] Mengatur host dan port saat menjalankan server.
- [ ] Membaca log server untuk melihat request yang masuk.
- [ ] Menjelaskan peran ASGI sebagai penghubung antara server dan aplikasi.
- [ ] Mengenali masalah umum saat menjalankan server, termasuk port yang sudah terpakai.

## Prasyarat

- Sudah membaca [Aplikasi Pertama](aplikasi-pertama.md), termasuk perbedaan aplikasi dan server.
- Venv aktif dan FastAPI terpasang, sesuai [Instalasi dan Virtual Environment](instalasi-dan-venv.md).

!!! info "Versi yang diuji"
    Perintah dan output di halaman ini dijalankan dengan **Python 3.14.7** dan **FastAPI 0.162.0** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep: alamat server

Alamat seperti `http://127.0.0.1:8000` tersusun dari beberapa bagian:

```text
http://127.0.0.1:8000/kesehatan
  │       │        │      └── path (dibahas di materi HTTP dan REST)
  │       │        └───────── port
  │       └────────────────── host
  └────────────────────────── skema (protokol)
```

| Bagian | Artinya |
|---|---|
| **Host** | Alamat komputer tempat server berjalan. `127.0.0.1` berarti komputermu sendiri |
| **Port** | Nomor "pintu" pada komputer itu. Satu komputer punya banyak port, dan tiap server memakai satu |

Host menentukan **siapa yang bisa terhubung**. Menurut bantuan perintah `fastapi`, `127.0.0.1` cocok untuk pengembangan di komputer sendiri, sedangkan `0.0.0.0` berarti seluruh alamat IP yang tersedia, misalnya agar bisa diakses dari luar kontainer.

## Konsep: ASGI, penghubung server dan aplikasi

Server dan aplikasi adalah dua program yang berbeda, jadi keduanya butuh kesepakatan tentang cara berkomunikasi. Untuk web Python yang bersifat asinkron, kesepakatan itu bernama **ASGI** (*Asynchronous Server Gateway Interface*).

Menurut dokumentasi ASGI, aplikasi ASGI tersusun sebagai satu *callable* asinkron, yaitu fungsi yang dipanggil server untuk setiap koneksi, dengan tiga argumen:

| Argumen | Isinya |
|---|---|
| `scope` | Dict berisi detail tentang koneksi tertentu |
| `receive` | Callable asinkron untuk menerima event dari klien |
| `send` | Callable asinkron untuk mengirim event ke klien |

Kamu tidak perlu menulis ketiganya. Pada pengujian, objek `FastAPI` ternyata memang fungsi *coroutine* (`__call__`) dengan argumen persis `scope`, `receive`, dan `send`, dan kelas `FastAPI` merupakan turunan dari `Starlette`. Artinya objek `app` yang kamu buat dapat langsung dipanggil oleh server ASGI, dan FastAPI mengurus bagian dalamnya.

```text
Klien ──request──▶ Server (Uvicorn) ──scope, receive, send──▶ app (FastAPI) ──▶ fungsi endpoint
Klien ◀─response── Server (Uvicorn) ◀──────── send ───────── app (FastAPI) ◀── hasil fungsi
```

Mengapa kesepakatan baku ini penting? Dokumentasi ASGI membandingkannya dengan WSGI, pendahulunya. WSGI berupa satu callable sinkron yang tidak mendukung koneksi berumur panjang seperti WebSocket, sedangkan ASGI mendukung banyak event masuk dan keluar. Format event yang baku membuat aplikasi dapat dipertukarkan antar server.

Uvicorn adalah server ASGI, itulah sebabnya ia menyebut "ASGI app" pada pesan kesalahan yang kamu lihat di [Aplikasi Pertama](aplikasi-pertama.md#kesalahan-umum). Perilaku `async` dan `await` pada endpoint dibahas di [Dasar Async/Await](../02-dasar-routing/async-await.md).

## Kode yang dipakai

Halaman ini memakai `main.py` yang sama dengan [Aplikasi Pertama](aplikasi-pertama.md), jadi tidak ada kode aplikasi baru. Simpan sebagai `main.py` bila belum ada:

```python title="main.py"
--8<-- "fastapi/01-pengenalan/aplikasi-pertama/main.py"
```

Yang dibahas di sini adalah **perintah menjalankannya**.

## Dua perintah: `fastapi dev` dan `fastapi run`

Keduanya menjalankan aplikasi yang sama, tetapi bawaannya berbeda. Tabel ini bersumber dari `--help` masing-masing perintah:

| | `fastapi dev` | `fastapi run` |
|---|---|---|
| Tujuan | Pengembangan di komputermu | Menjalankan aplikasi untuk dipakai |
| Host bawaan | `127.0.0.1` | `0.0.0.0` |
| Reload otomatis | Aktif | Nonaktif |
| `--workers` | Tidak ada | Ada (tidak bisa bersama `--reload`) |

Penjelasan bantuan perintah menyebut reload otomatis memakai banyak sumber daya sehingga hanya cocok saat pengembangan. Materi ini memakai `fastapi dev`. Penggunaan `fastapi run` di produksi dibahas di [Modul 10](../10-deployment/index.md).

## Opsi yang sering dipakai

| Opsi | Fungsinya | Contoh |
|---|---|---|
| `--port` | Nomor port | `--port 9000` |
| `--host` | Alamat yang didengarkan | `--host 0.0.0.0` |
| `--no-reload` / `--reload` | Mematikan atau menyalakan reload otomatis | |
| `--entrypoint` / `-e` | Import string, bentuk `modul:variabel` | `-e main:app` |
| `--app` | Nama variabel aplikasi di modul | `--app app` |

Pada pengujian, opsi `--port` dan `--host` diuji langsung. Opsi lain di atas hanya dibaca dari `--help` dan **belum saya jalankan**.

## Menjalankan server

Pastikan terminal berada di folder `main.py` dan venv aktif.

### Mode pengembangan

```bash
fastapi dev main.py
```

Pada pengujian dengan `--port 8782`, log menampilkan (cuplikan):

```text
Using import string: main:app
Server started at http://127.0.0.1:8782
Documentation at http://127.0.0.1:8782/docs
INFO:     Will watch for changes in these directories: [...]
INFO:     Uvicorn running on http://127.0.0.1:8782 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

Tanpa `--port`, port bawaannya `8000`. Baris `Press CTRL+C to quit` memberi tahu cara berhenti: tekan `Ctrl+C` di terminal tempat server berjalan.

### Mengganti port

```bash
fastapi dev main.py --port 9000
```

Alamat servernya berubah mengikuti port: `http://127.0.0.1:9000`. Gunakan opsi ini bila port bawaan sudah dipakai program lain.

### Mengubah host

```bash
fastapi dev main.py --host 0.0.0.0 --port 9000
```

Pada pengujian (dengan port 8781), log menampilkan `Uvicorn running on http://0.0.0.0:8781`. Dari komputer yang sama, server tetap dapat dipanggil lewat `http://127.0.0.1:8781`.

!!! warning "Perhatikan keamanan"
    Dengan `0.0.0.0`, perangkat lain di jaringanmu berpotensi dapat mengakses server. Pengujian saya hanya dari komputer yang sama; akses dari perangkat lain **belum diuji**, begitu pula pengaruh firewall. Pakai `127.0.0.1` selama belajar.

### Mode `run`

```bash
fastapi run main.py --port 9000
```

Pada pengujian (dengan port 8780), log menampilkan `Server started at http://0.0.0.0:8780` dan tidak ada baris `Will watch for changes`, sesuai tabel di atas.

## Membaca log

Setiap request yang masuk dicatat server. Hasil dari eksekusi nyata setelah empat request:

```text
INFO:     127.0.0.1:57830 - "GET / HTTP/1.1" 200 OK
INFO:     127.0.0.1:57831 - "GET /kesehatan HTTP/1.1" 200 OK
INFO:     127.0.0.1:57832 - "GET /tidak-ada HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:57833 - "POST / HTTP/1.1" 405 Method Not Allowed
```

| Bagian baris | Artinya |
|---|---|
| `127.0.0.1:57830` | Alamat dan port klien yang mengirim request. Port klien berganti-ganti |
| `"GET / HTTP/1.1"` | Method, path, dan versi HTTP |
| `200 OK` | Status code response |

Log ini membantu saat kamu bertanya "apakah request-ku benar-benar sampai?". Status code dijelaskan di [HTTP dan REST](http-dan-rest.md).

## Mencoba request

Dengan server berjalan di port 9000, gunakan terminal kedua (pengguna PowerShell: ketik `curl.exe`):

```bash
curl -i http://127.0.0.1:9000/
curl -i http://127.0.0.1:9000/kesehatan
```

Hasil yang diharapkan sama dengan di [Aplikasi Pertama](aplikasi-pertama.md): `200 OK` dengan `{"pesan":"Aplikasi pertama berjalan!"}` dan `{"status":"ok"}`. Pengujian halaman ini mengonfirmasi `/kesehatan` dan `/` pada beberapa port yang berbeda.

## Kesalahan umum

Semua kasus berikut dijalankan dan dicatat apa adanya.

### 1. Dua server memakai host dan port yang sama

Dua `fastapi dev main.py --port 8782` dijalankan berurutan. Server kedua **menyala tanpa pesan kesalahan**; log-nya menampilkan `Uvicorn running on http://127.0.0.1:8782` dan `Application startup complete`. Server pertama tetap hidup.

Ini berbahaya karena tidak ada peringatan: request bisa dilayani server lama yang kodenya sudah usang, sehingga perubahanmu terasa "tidak berpengaruh". Perilaku ini teramati di Windows; sistem operasi lain **belum diuji** dan bisa saja menolak dengan galat.

**Solusi:** pastikan hanya ada satu server per port. Hentikan server lama dengan `Ctrl+C` sebelum menjalankan yang baru, atau pilih port lain dengan `--port`.

### 2. Server berjalan, tetapi alamat salah

Jika server dijalankan dengan `--port 9000` tetapi kamu membuka `http://127.0.0.1:8000`, kamu tidak akan terhubung ke server itu. **Solusi:** baca baris `Server started at ...` pada log dan pakai alamat persis seperti itu.

### 3. Terminal ditutup, server mati

Server hidup selama proses di terminal berjalan. Menekan `Ctrl+C` atau menutup terminal menghentikannya. **Solusi:** biarkan terminal server tetap terbuka, dan pakai terminal kedua untuk `curl`.

### 4. Server tidak dapat dihubungi setelah dihentikan

Setelah server dihentikan, `curl` ke alamat tadi gagal terhubung (pada pengujian, kode status HTTP `000` dan `curl` keluar dengan kode 7). Itu normal: tidak ada lagi server yang menjawab.

## Latihan

1. **Dasar.** Jalankan `fastapi dev main.py --port 9000`. Buka `http://127.0.0.1:9000/kesehatan` dan pastikan jawabannya `{"status":"ok"}`.
2. **Menengah.** Kirim request ke path yang tidak ada, misalnya `/tidak-ada`, lalu cari barisnya di log. Status apa yang tercatat?
3. **Menengah.** Dari tabel perbandingan, tentukan perintah mana yang menyala di `127.0.0.1` bila host tidak disebutkan, dan mana yang di `0.0.0.0`.
4. **Tantangan.** Jelaskan dengan kata-katamu sendiri mengapa `--host 0.0.0.0` perlu dipertimbangkan dari sisi keamanan, dan kapan ia berguna.
5. **Menengah.** Pesan `Error loading ASGI app. Attribute "salah" not found in module "main".` berasal dari program mana, dan apa artinya?

??? success "Petunjuk jawaban"
    1. Hasil yang diharapkan: `{"status":"ok"}` dengan status `200 OK`.
    2. Pada pengujian, baris log-nya `127.0.0.1:... - "GET /tidak-ada HTTP/1.1" 404 Not Found`.
    3. `fastapi dev` bawaannya `127.0.0.1`, `fastapi run` bawaannya `0.0.0.0` (dari `--help` masing-masing).
    4. `0.0.0.0` membuat server mendengarkan semua alamat IP komputer, sehingga perangkat lain di jaringan berpotensi dapat mengaksesnya. Ini berguna misalnya di dalam kontainer, tetapi tidak perlu saat belajar di komputer sendiri.
    5. Pesan itu dicetak oleh Uvicorn (teramati saat menjalankan `python -m uvicorn main:salah`). Artinya server tidak menemukan variabel bernama `salah` di dalam file `main.py`, jadi tidak ada aplikasi ASGI yang bisa dimuat. Perbaiki bagian setelah titik dua pada import string.

## Ringkasan

- Alamat server terdiri dari host, port, dan path. Host menentukan siapa yang bisa terhubung.
- `fastapi dev` untuk pengembangan (host `127.0.0.1`, reload aktif), `fastapi run` untuk menjalankan aplikasi (host `0.0.0.0`, reload mati).
- Ubah port dengan `--port` dan host dengan `--host`.
- Log mencatat tiap request beserta status code-nya, dan `Ctrl+C` menghentikan server.
- ASGI adalah kesepakatan antara server dan aplikasi: aplikasi berupa callable asinkron berargumen `scope`, `receive`, dan `send`. Objek `FastAPI` memenuhinya, sehingga bisa dijalankan Uvicorn.
- Hati-hati: di Windows, server kedua dengan host dan port yang sama bisa menyala tanpa error. Pastikan hanya satu server per port.

## Langkah berikutnya

Lanjutkan ke [Endpoint Pertama](endpoint-pertama.md), atau kembali ke [Modul 01: Pengenalan](index.md).
