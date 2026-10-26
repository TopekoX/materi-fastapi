# Logging

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan mengapa produksi memakai *logging* (catatan terstruktur), bukan `print()`.
- [ ] Memakai modul `logging` bawaan Python: *logger*, *level*, *handler*, *formatter*, dan *filter*.
- [ ] Mengatur logging dari satu fungsi dengan `dictConfig`, dengan level dan format yang dipilih lewat variabel environment.
- [ ] Menempelkan **request ID** ke setiap catatan lewat middleware dan `ContextVar`.
- [ ] Mencatat galat beserta jejak stack-nya dengan `log.exception`.
- [ ] Menyamarkan data rahasia di log, dan mengenali celah yang **tidak** tertutup oleh filter.

## Prasyarat

- Sudah membaca [Middleware](../08-struktur-proyek/middleware.md) dan [Variabel Environment](variabel-environment.md).
- Sudah membaca [Server Produksi](server-produksi.md), karena contoh dijalankan dengan `fastapi run`.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **Uvicorn 0.54.0**, dan **pytest 9.1.1** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**. Pengiriman log ke layanan pengumpul (misalnya ELK, Loki, atau layanan cloud) **tidak diuji**.

## Konsep

*Log* adalah catatan kejadian yang ditulis aplikasi saat berjalan. Di produksi kamu tidak duduk di depan terminal, jadi log adalah satu-satunya cara tahu apa yang terjadi: siapa memanggil apa, kapan, berapa lama, dan mengapa gagal.

`print()` tidak cukup karena tidak punya tingkat penting-tidaknya, tidak punya waktu, tidak bisa dimatikan sebagian, dan tidak bisa diarahkan ke tempat lain tanpa mengubah kode. Modul `logging` bawaan Python menyelesaikan itu.

### Lima komponen `logging`

| Komponen | Peran |
|---|---|
| **Logger** | Objek yang dipanggil kode kamu (`log.info(...)`). Namanya berhierarki dengan titik: `tugasku.aplikasi` adalah anak dari `tugasku`. |
| **Level** | Tingkat penting: `DEBUG` < `INFO` < `WARNING` < `ERROR` < `CRITICAL`. Catatan di bawah level yang diatur dibuang. |
| **Handler** | Tujuan catatan (konsol, berkas, jaringan). |
| **Formatter** | Bentuk tulisan sebuah catatan (teks atau JSON). |
| **Filter** | Kode kecil yang boleh menambah atau mengubah catatan, atau membuangnya. |

Di kontainer, cara yang disarankan adalah menulis log ke **keluaran standar** (stdout) dan membiarkan platform yang mengumpulkannya. Aplikasi tidak perlu mengelola berkas log sendiri.

### Kapan memakai level apa

| Level | Contoh |
|---|---|
| `DEBUG` | Detail untuk pengembang; biasanya mati di produksi. |
| `INFO` | Kejadian normal yang penting: request selesai, aplikasi mulai. |
| `WARNING` | Ada yang janggal tetapi aplikasi tetap jalan. |
| `ERROR` | Operasi gagal. |
| `CRITICAL` | Aplikasi tidak bisa melanjutkan. |

## Kode lengkap

Contoh ada di `examples/fastapi/10-deployment/logging/`.

### `pengaturan_log.py`

```python title="pengaturan_log.py"
--8<-- "fastapi/10-deployment/logging/pengaturan_log.py"
```

### `main.py`

```python title="main.py"
--8<-- "fastapi/10-deployment/logging/main.py"
```

## Penjelasan kode

### `request_id_var`

`ContextVar` adalah variabel yang nilainya terpisah untuk setiap alur eksekusi. Pada kode async, banyak request berjalan bergantian di satu proses; dengan `ContextVar`, nilai milik request A tidak tertukar dengan request B. Bawaannya `"-"` untuk catatan di luar request, misalnya saat aplikasi mulai.

### `FilterRequestId`

Filter ini dipanggil untuk setiap catatan dan menambahkan atribut `request_id` yang diambil dari `ContextVar`. Atribut itu lalu bisa dipakai di format dengan `%(request_id)s`. Filter mengembalikan `True` artinya "catatan ini diteruskan".

### `FilterRahasia` dan `POLA_RAHASIA`

`POLA_RAHASIA` adalah ekspresi reguler yang mencari kata seperti `kata_sandi`, `password`, `token`, `authorization`, atau `secret_key` diikuti `=` atau `:` lalu sebuah nilai. Filter mengganti nilainya dengan `***`. Pesan dirakit lebih dulu dengan `getMessage()` supaya argumen `%s` ikut diperiksa, lalu `args` dikosongkan agar pesan tidak dirakit dua kali.

!!! warning "Filter ini jaring pengaman, bukan izin untuk mencatat rahasia"
    Pola hanya mengenal nama yang ada di daftar. Nilai rahasia dengan nama lain tetap lolos. Aturan utamanya: **jangan memasukkan rahasia ke pesan log sejak awal**. Lihat juga bagian [Celah: log akses Uvicorn](#celah-log-akses-uvicorn).

### `FormatJson`

Formatter ini menghasilkan **satu baris JSON** per catatan: waktu (UTC), level, nama logger, request ID, pesan, dan, bila ada galat, jejak stack di kunci `galat`. Satu baris satu objek memudahkan alat pengumpul log memecah dan mencarinya. `ensure_ascii=False` mempertahankan huruf non-ASCII.

### `atur_logging`

Fungsi ini memanggil `logging.config.dictConfig` dengan sebuah kamus yang mendeskripsikan seluruh konfigurasi:

- `disable_existing_loggers: False` agar logger milik pustaka lain (termasuk Uvicorn) tidak dimatikan.
- `filters` mendaftarkan dua filter di atas; `"()"` berarti "buat objek dari kelas ini".
- `formatters` berisi format `teks` dan `json`.
- `handlers.konsol` menulis ke `sys.stdout` dan memasang kedua filter.
- `loggers.tugasku` mengatur logger induk aplikasi: level dari parameter dan `propagate: False` supaya catatan tidak diulang oleh logger induk (`root`).

### `main.py`

- Level dan format dibaca dari `TUGASKU_LOG_LEVEL` dan `TUGASKU_LOG_FORMAT`, dengan bawaan `INFO` dan `teks`. Dengan begitu produksi bisa mengubahnya tanpa mengubah kode.
- `logging.getLogger("tugasku.aplikasi")` membuat logger anak dari `tugasku`, sehingga otomatis memakai handler dan level yang sudah diatur.
- Middleware `catat_request` menentukan request ID (memakai header `X-Request-ID` kiriman klien bila ada, atau membuat sendiri), menyimpannya ke `ContextVar`, mengukur durasi, mencatat satu baris per request, dan mengembalikan ID itu di header respons. Bagian `except` mencatat galat tak terduga dengan `log.exception` lalu melempar ulang galatnya. Bagian `finally` mengembalikan `ContextVar` ke nilai semula.
- `log.exception(...)` dimaksudkan untuk dipanggil di dalam blok `except` (di sanalah galat yang sedang ditangani tersedia): ia mencatat pesan dengan level `ERROR` **ditambah jejak stack**.
- Endpoint `/masuk` sengaja mencatat kata sandi untuk memperlihatkan filter. **Jangan meniru ini.**

!!! note "Format pesan memakai `%s`, bukan f-string"
    `log.info("... %s", nilai)` menunda perakitan pesan sampai catatan benar-benar dipakai. Pesan yang levelnya dibuang tidak membayar biaya perakitan. Ini juga cara yang dipakai dokumentasi Python.

## Menjalankan

Pasang dependensi contoh (lihat [Instalasi dan Venv](../01-pengenalan/instalasi-dan-venv.md)), lalu dari folder contoh:

```powershell
cd examples\fastapi\10-deployment\logging
$env:TUGASKU_LOG_LEVEL = "DEBUG"
fastapi run main.py --port 8961
```

Format JSON, tanpa log akses Uvicorn:

```powershell
$env:TUGASKU_LOG_FORMAT = "json"
python -m uvicorn main:app --port 8962 --no-access-log
```

## Mencoba

Kamu bisa memakai `curl` atau halaman `/docs`. Perintah berikut dan keluarannya berasal dari eksekusi nyata dengan `TUGASKU_LOG_LEVEL=DEBUG`.

```powershell
curl.exe -i http://127.0.0.1:8961/kerja
```

Respons memuat header `x-request-id: 805f1199` (nilainya acak setiap kali) dan isi `{"selesai":true}`. Di terminal server muncul:

```text
2026-10-26 21:53:30,711 DEBUG    [805f1199] tugasku.aplikasi: mulai bekerja (tingkat DEBUG)
2026-10-26 21:53:30,711 INFO     [805f1199] tugasku.aplikasi: pekerjaan sedang berjalan
2026-10-26 21:53:30,711 WARNING  [805f1199] tugasku.aplikasi: sumber daya hampir penuh
2026-10-26 21:53:30,711 INFO     [805f1199] tugasku.aplikasi: GET /kerja -> 200 (1.5 ms)
INFO:     127.0.0.1:56339 - "GET /kerja HTTP/1.1" 200 OK
```

Perhatikan: keempat catatan pertama memakai format kita dan membawa request ID yang sama, sedangkan baris `INFO:     127.0.0.1...` datang dari Uvicorn dengan format sendiri.

### Galat yang ditangani

`GET /gagal-tertangani` mengembalikan `400`. Log-nya memuat jejak stack:

```text
2026-10-26 21:53:30,775 ERROR    [66fea31e] tugasku.aplikasi: pembagian dengan nol
Traceback (most recent call last):
  File ".../main.py", line 55, in gagal_tertangani
    return 1 / 0
           ~~^~~
ZeroDivisionError: division by zero
2026-10-26 21:53:30,775 INFO     [66fea31e] tugasku.aplikasi: GET /gagal-tertangani -> 400 (0.9 ms)
```

(Jalur berkas dipersingkat di sini; nomor baris mengikuti berkas saat dijalankan.)

### Galat tak terduga

`GET /gagal-tak-terduga` mengembalikan `500`. Di log muncul **dua** laporan galat: satu dari middleware kita (`request gagal: GET /gagal-tak-terduga` beserta jejak stack, memakai request ID) dan satu dari Uvicorn (`ERROR:    Exception in ASGI application`, tanpa request ID). Hasilnya jejak stack tercatat dua kali. Itu perilaku nyata dari pengujian ini; kamu bisa memilih untuk tidak mencatat ulang di middleware bila Uvicorn sudah mencatatnya, dengan konsekuensi catatan itu tidak membawa request ID.

### Format JSON

Dengan `TUGASKU_LOG_FORMAT=json` dan header `X-Request-ID: tes-001`:

```text
{"waktu": "2026-10-26T13:54:03.882+00:00", "level": "INFO", "logger": "tugasku.aplikasi", "request_id": "tes-001", "pesan": "pekerjaan sedang berjalan"}
{"waktu": "2026-10-26T13:54:03.882+00:00", "level": "WARNING", "logger": "tugasku.aplikasi", "request_id": "tes-001", "pesan": "sumber daya hampir penuh"}
{"waktu": "2026-10-26T13:54:03.883+00:00", "level": "INFO", "logger": "tugasku.aplikasi", "request_id": "tes-001", "pesan": "GET /kerja -> 200 (1.5 ms)"}
```

Request ID dari klien dipakai apa adanya, jadi satu permintaan bisa dilacak dari klien sampai ke log. (Baris log Uvicorn saat mulai, `INFO:     Started server process ...`, tetap berupa teks biasa di keluaran yang sama. Lihat bagian berikut.)

### Celah: log akses Uvicorn

Perintah ini mengirim kata sandi di *query string*:

```powershell
curl.exe -s -X POST "http://127.0.0.1:8961/masuk?nama_pengguna=budi&kata_sandi=RAHASIA-123"
```

Log kita menyamarkannya:

```text
2026-10-26 21:53:30,821 INFO     [24483a4c] tugasku.aplikasi: percobaan masuk nama_pengguna=budi kata_sandi=***
```

Tetapi log akses Uvicorn pada saat yang sama menulis:

```text
INFO:     127.0.0.1:56342 - "POST /masuk?nama_pengguna=budi&kata_sandi=RAHASIA-123 HTTP/1.1" 200 OK
```

Filter kita hanya terpasang pada logger `tugasku`, sehingga **kata sandi bocor lewat log milik Uvicorn**. Pelajaran dari temuan ini:

1. **Jangan pernah mengirim rahasia lewat URL** (path atau query string). Kirim lewat badan request atau header, seperti yang dilakukan [Token](../07-autentikasi-keamanan/token.md).
2. Server, proksi, dan CDN umumnya mencatat URL lengkap. Menyamarkan di aplikasi saja tidak cukup.
3. Bila perlu, matikan log akses (`--no-access-log` pada `uvicorn`) dan andalkan satu baris per request dari middleware kita.

## Mengatur log Uvicorn

`fastapi run` hanya punya opsi `--verbose`/`-v` untuk log, dan tidak menerima `--log-level` atau `--log-config`. Menurut `--help` Uvicorn, opsi yang tersedia di `uvicorn` adalah `--log-config PATH`, `--log-level` (`critical`, `error`, `warning`, `info`, `debug`, `trace`; bawaan `info`), `--access-log/--no-access-log`, dan `--use-colors/--no-use-colors`. Jika kamu ingin seluruh log (termasuk milik Uvicorn) berbentuk JSON, jalankan dengan `uvicorn` dan berikan `--log-config`. Cara membuat berkas konfigurasinya **tidak dibahas dan tidak diuji** di halaman ini.

## Pengujian

Berkas `test_logging.py` berisi 9 pengujian. Hasil nyata:

```text
9 passed in 0.33s
```

Pengujian memeriksa: baris request memuat metode, path, status, dan durasi; request ID dari header dipakai dan dikembalikan; ID dibuat bila tidak ada; level `WARNING` tercatat; kata sandi disamarkan di keluaran; `log.exception` menulis jejak stack; galat tak terduga menjadi `500` dan tercatat; format JSON valid per baris; dan level `WARNING` menyembunyikan `INFO`.

Dua pemeriksaan mutasi dilakukan untuk memastikan pengujian benar-benar menangkap kesalahan:

- Filter rahasia dicabut dari handler: `test_kata_sandi_disamarkan_di_keluaran` gagal.
- Request ID dipaksa tetap `"-"`: dua pengujian gagal (ID dari header dan format JSON).

Sebuah mutasi ketiga, menghapus `request_id_var.reset(token)`, **tidak** menggagalkan pengujian apa pun. Jadi pemanggilan `reset` tidak dilindungi pengujian; ia dipertahankan sebagai kebiasaan yang rapi, bukan karena terbukti diperlukan di sini.

!!! tip "Tentang menangkap keluaran di pytest"
    Handler menyimpan objek `sys.stdout` pada saat dikonfigurasi. Karena itu `capsys` tidak menangkap isinya (percobaan pertama gagal karena ini). Pengujian di sini mengarahkan handler ke `io.StringIO` dengan `setStream`.

## Kesalahan umum

| Kesalahan | Penjelasan |
|---|---|
| Memakai `print()` di produksi | Tidak ada level, waktu, atau pengenal request. |
| Mencatat rahasia, token, atau data pribadi | Log disalin ke banyak tempat dan jarang dilindungi seketat basis data. |
| Rahasia di URL | Muncul di log akses server dan proksi (terbukti di atas). |
| `log.error(str(e))` di dalam `except` | Jejak stack hilang. Pakai `log.exception(...)`. |
| Merakit pesan dengan f-string di setiap catatan | Biaya dibayar walau levelnya dibuang. Pakai `%s` dan argumen. |
| Level `DEBUG` di produksi | Volume besar dan bisa memuat detail sensitif. |
| Menulis log ke berkas di dalam container tanpa volume | Hilang saat container diganti. Tulis ke stdout. |
| Memanggil `dictConfig` di dalam handler request | Konfigurasi dilakukan sekali saat mulai. |

## Latihan

1. **Dasar.** Sebutkan kelima level dari yang paling rendah, dan satu contoh kejadian untuk `WARNING`.
2. **Prediksi.** Dengan `TUGASKU_LOG_LEVEL=WARNING`, baris apa dari `GET /kerja` yang masih muncul di log aplikasi kita?
3. **Praktik.** Tambahkan field `metode` dan `path` sebagai kunci terpisah di `FormatJson` (bukan hanya di dalam `pesan`). Apa yang perlu kamu kirim ke `log.info` agar nilainya tersedia di `record`?
4. **Analisis.** Mengapa menyamarkan `kata_sandi` di logger aplikasi saja tidak menjamin kata sandi tidak masuk log?

??? success "Kunci jawaban"
    1. `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. Contoh `WARNING`: sumber daya hampir penuh, seperti di `/kerja`.
    2. Hanya `sumber daya hampir penuh` (level `WARNING`). Catatan `INFO` dan `DEBUG` dibuang (teruji pada `test_level_warning_menyembunyikan_info`).
    3. Gunakan argumen `extra`, misalnya `log.info("...", extra={"metode": ..., "path": ...})`; kuncinya menjadi atribut `record.metode` dan `record.path`. Lalu tambahkan `getattr(record, "metode", None)` ke kamus di `FormatJson`. Jawaban ini adalah penerapan dokumentasi `logging` dan tidak dijalankan di halaman ini.
    4. Log akses Uvicorn dan komponen lain (proksi, CDN) mencatat URL lengkap dengan loggernya sendiri; filter kita hanya terpasang pada logger `tugasku` (terbukti: `kata_sandi=RAHASIA-123` muncul di baris `INFO:     127.0.0.1...`).

## Ringkasan

- Log adalah mata kita di produksi; tulis ke stdout dan biarkan platform mengumpulkannya.
- `logging` punya logger, level, handler, formatter, dan filter; satu fungsi `dictConfig` cukup untuk mengatur semuanya.
- Level dan format dipilih lewat environment, bukan dengan mengubah kode.
- Request ID lewat middleware dan `ContextVar` membuat satu permintaan bisa dilacak di semua baris log.
- `log.exception` mencatat jejak stack; format JSON memudahkan mesin membaca log.
- Jangan mencatat rahasia, dan jangan mengirim rahasia lewat URL: log akses server tidak tersentuh filter aplikasi.

## Langkah berikutnya

Lanjut ke [Reverse Proxy dan HTTPS](reverse-proxy-https.md), atau kembali ke daftar materi di [Modul 10: Deployment](index.md).
