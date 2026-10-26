# Server Produksi

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Membedakan `fastapi dev` dan `fastapi run`, serta alasan `--reload` tidak dipakai di produksi.
- [ ] Menjalankan aplikasi dengan `fastapi run` dan `uvicorn` langsung.
- [ ] Menjelaskan apa itu *worker* dan kapan beberapa proses berguna.
- [ ] Membuktikan dengan pengukuran bahwa beberapa proses mempercepat pekerjaan CPU yang berat.
- [ ] Menjelaskan konsekuensi worker terhadap data yang disimpan di memori.
- [ ] Memilih alamat `host` yang tepat dan mengenali peran proksi di depan aplikasi.

## Prasyarat

- Sudah membaca [Menjalankan Server](../01-pengenalan/menjalankan-server.md) dan [Dasar Async/Await](../02-dasar-routing/async-await.md).
- Sudah membaca [Lifespan](../08-struktur-proyek/lifespan.md) dan [Pengujian Endpoint](../09-pengujian/pengujian-endpoint.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **FastAPI CLI 0.0.32**, **Uvicorn 0.54.0**, dan **httpx 0.28.1** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**. Hasil pengukuran waktu bergantung pada mesin (di sini 24 prosesor logis).

## Konsep

### Mesin pengembangan dan mesin produksi

Selama belajar, kita menjalankan aplikasi dengan `fastapi dev`. Itu cocok untuk pengembangan, tetapi tidak untuk melayani pengguna sungguhan. Menurut dokumentasi FastAPI, produksi dilayani dengan `fastapi run`, dan opsi `--reload` tidak boleh dipakai di produksi karena memakan sumber daya jauh lebih banyak dan kurang stabil.

| | `fastapi dev` | `fastapi run` |
|---|---|---|
| Tujuan | pengembangan | produksi |
| Muat ulang otomatis saat kode berubah (`--reload`) | **ya** (bawaan) | **tidak** (bawaan) |
| Banyak proses (`--workers`) | tidak ada opsinya | ada |
| Alamat (`host`) bawaan | `127.0.0.1` (hanya komputer sendiri) | `0.0.0.0` menurut dokumentasi FastAPI (semua alamat) |

Nilai bawaan `--reload` di kedua perintah terbaca di `--help` masing-masing (`dev`: reload, `run`: no-reload). Alamat bawaan `fastapi run` bersumber dari dokumentasi FastAPI; saya tidak menjalankannya pada `0.0.0.0` dan selalu memakai `--host 127.0.0.1` di halaman ini.

### Server ASGI

FastAPI hanyalah kerangka aplikasi. Untuk menerima koneksi jaringan, ia butuh **server ASGI** ([Menjalankan Server](../01-pengenalan/menjalankan-server.md) menjelaskan ASGI). **Uvicorn** adalah server bawaan yang dipakai `fastapi run`. Dokumentasi FastAPI juga menyebut Hypercorn, Daphne, dan Granian; ketiganya tidak dibahas atau diuji di sini.

### Host, port, dan proksi di depan aplikasi

- `--host 127.0.0.1` hanya menerima koneksi dari komputer yang sama. `--host 0.0.0.0` menerima koneksi dari semua alamat jaringan. Teks `--help` mengatakan alamat publik (misalnya di dalam container) memakai semua alamat IP yang tersedia.
- Teks `--help` untuk `--port` menyebut bahwa kamu biasanya punya *termination proxy* di depan aplikasi: program lain yang menangani HTTPS di port 443 dan HTTP di port 80, lalu meneruskan ke aplikasimu. Aplikasi sendiri tidak harus mengurus sertifikat HTTPS.
- Karena ada proksi di depan, aplikasi perlu membaca alamat asli klien dari header `X-Forwarded-*`. `fastapi run` dan `fastapi dev` memiliki opsi `--proxy-headers` (aktif bawaan) dan `--forwarded-allow-ips` untuk menentukan alamat proksi yang dipercaya. `*` berarti percaya semua. Pengaturan ini tidak diuji di sini.

## Kode lengkap

Contoh ada di `examples/fastapi/10-deployment/server-produksi/`.

### `main.py`

```python title="main.py"
--8<-- "fastapi/10-deployment/server-produksi/main.py"
```

- `GET /info` mengembalikan nomor proses (*PID*) yang melayani request.
- `GET /hitung` menjalankan pekerjaan yang benar-benar memakai CPU dengan jumlah langkah tetap (`n` pengulangan). Ini mewakili komputasi berat.
- `POST /kunjungan` menaikkan penghitung di memori dan mengembalikan nilainya bersama PID.

### `ukur_paralel.py` dan `ukur_kunjungan.py`

```python title="ukur_paralel.py"
--8<-- "fastapi/10-deployment/server-produksi/ukur_paralel.py"
```

```python title="ukur_kunjungan.py"
--8<-- "fastapi/10-deployment/server-produksi/ukur_kunjungan.py"
```

## Menjalankan

```powershell
fastapi run main.py --host 127.0.0.1 --port 8000
```

Hasil sebenarnya:

```text
 Server started at http://127.0.0.1:8941
 Documentation at http://127.0.0.1:8941/docs
INFO:     Uvicorn running on http://127.0.0.1:8941 (Press CTRL+C to quit)
```

(Port 8941 dipakai saat pengujian, dan emoji pada baris pertama dihilangkan.) Untuk beberapa proses:

```powershell
fastapi run main.py --host 127.0.0.1 --port 8000 --workers 4
```

```text
INFO:     Uvicorn running on http://127.0.0.1:8942 (Press CTRL+C to quit)
INFO:     Started parent process [29876]
INFO:     Started server process [21444]
INFO:     Started server process [30068]
INFO:     Started server process [23812]
INFO:     Started server process [18672]
```

Terlihat satu **proses induk** (pengelola) dan empat **proses server**, masing-masing melayani request. Uvicorn langsung juga bisa:

```powershell
uvicorn main:app --host 127.0.0.1 --port 8000 --workers 2
```

```text
INFO:     Uvicorn running on http://127.0.0.1:8943 (Press CTRL+C to quit)
INFO:     Started parent process [14108]
INFO:     Started server process [22008]
INFO:     Started server process [14592]
```

Pada `uvicorn`, `main` adalah berkas `main.py` dan `app` adalah objek `FastAPI` di dalamnya. Dokumentasi FastAPI menyebut bahwa dengan `[standard]` terpasang `uvloop`, pengganti *event loop* yang lebih cepat; hal itu tidak diukur di sini.

!!! warning "`--workers` dan `--reload` tidak bisa dipakai bersama"
    Teks `--help` untuk `--workers` menyatakan opsi itu "mutually exclusive with the `--reload` flag" (saling meniadakan). Pada percobaan memakai `uvicorn main:app --reload --workers 2`, proses tidak menghasilkan keluaran dalam batas waktu percobaan (dihentikan), jadi hasilnya tidak bisa dijadikan acuan; hindari kombinasi itu.

## Mencoba

### Beberapa proses mempercepat pekerjaan CPU berat

`GET /hitung` dijalankan sekali: sekitar 1,2 detik di server (`1.23` pada satu proses, `1.26` pada empat). Lalu empat request dikirim **bersamaan** dengan `ukur_paralel.py`:

| Jumlah proses (`--workers`) | Total waktu empat request | Lama tiap request di server | Proses berbeda |
|---|---|---|---|
| 1 | **4,94 detik** | 4,45 sampai 4,59 detik | 1 |
| 4 | **1,33 detik** | 1,24 sampai 1,27 detik | 4 |

Dengan satu proses, empat request CPU berat harus antre berbagi satu prosesor, sehingga masing-masing terasa 4 kali lebih lama. Dengan empat proses, keempatnya berjalan paralel, masing-masing di prosesornya, dan total waktunya hampir sama dengan satu request. Inilah **replikasi**: beberapa salinan aplikasi yang berjalan bersamaan.

!!! note "Percobaan pertama yang keliru"
    Percobaan awal memakai *loop* yang menunggu 0,5 detik berdasarkan jam dinding. Hasilnya menyesatkan (empat request selesai 0,85 detik pada satu proses), karena menunggu berdasarkan jam tidak memakai CPU. Pekerjaan CPU yang sungguhan harus berupa **jumlah langkah tetap**, seperti `n` pengulangan di `/hitung`. Ukuran yang menipu seperti ini mudah terjadi, jadi periksa dulu apakah pekerjaannya benar-benar CPU.

Perlu dicatat juga: beberapa proses menolong untuk pekerjaan **CPU**. Untuk pekerjaan yang hanya menunggu (basis data, jaringan), `async` dan `await` sudah memberi paralelisme dalam satu proses ([Dasar Async/Await](../02-dasar-routing/async-await.md)); keuntungannya tidak diukur di sini.

### Request tersebar ke beberapa proses

Pada empat proses, enam request `GET /info` dijawab oleh proses dengan PID berbeda-beda:

```text
{"pid":23812}
{"pid":30068}
{"pid":23812}
{"pid":30068}
{"pid":21444}
{"pid":18672}
```

Pada satu proses, semuanya berPID sama (`24692`). Pembagian ke proses dilakukan sistem operasi, jadi tidak merata atau dapat diramalkan: pada percobaan lain dengan tiga proses, enam request berurutan yang dikirim satu per satu bisa saja semuanya jatuh ke proses yang sama.

### Konsekuensi: data di memori tidak dibagi antar proses

Dengan `ukur_kunjungan.py`, 12 request `POST /kunjungan` dikirim sekaligus:

| Jumlah proses | Hasil |
|---|---|
| 1 | penghitung terakhir `[12]`, jumlahnya 12 |
| 3 | penghitung terakhir `[1, 3, 8]`, jumlahnya 12 |

Dengan tiga proses, setiap proses punya penghitung sendiri, jadi tidak ada satu nilai "kunjungan" yang benar (pembagiannya berubah-ubah tiap percobaan). Ini berlaku untuk **semua** data yang disimpan di variabel Python, termasuk `dict` penyimpanan di modul-modul awal materi ini dan daftar token yang dicabut di [Refresh Token dan Pencabutan](../07-autentikasi-keamanan/refresh-token.md). Dengan beberapa proses, data bersama harus disimpan di luar memori proses: basis data (Modul 06), bukan variabel.

### Gunicorn di Windows

Dokumentasi FastAPI membahas Gunicorn dengan worker Uvicorn sebagai alternatif pengelola proses. Perintahnya (dengan paket `gunicorn` dan `uvicorn-worker`):

```powershell
gunicorn -w 4 -k uvicorn_worker.UvicornWorker main:app
```

Di Windows ini **tidak berjalan**: hasil sebenarnya setelah memasang `gunicorn` 26.2.0 dan `uvicorn-worker` 0.4.0:

```text
    import fcntl
ModuleNotFoundError: No module named 'fcntl'
```

Gunicorn bergantung pada modul `fcntl` yang hanya ada di sistem berbasis Unix (Linux, macOS). Di Windows, pakai `fastapi run --workers` atau `uvicorn --workers`. Perintah Gunicorn di atas tidak diuji di Linux atau macOS.

### Dokumentasi otomatis

`/docs` tetap tersedia di `fastapi run` (log menampilkan `Documentation at http://.../docs`). Tampilan visual Swagger UI **belum diverifikasi** lewat browser. Di produksi, pertimbangkan apakah dokumentasi interaktif perlu terbuka; pembahasannya ada di [Checklist Rilis](checklist-rilis.md).

## Kapan memakai beberapa proses

| Situasi | Saran |
|---|---|
| Satu server dengan beberapa inti CPU, pekerjaan CPU berat | `--workers` kira-kira sejumlah inti (mulai kecil dan ukur) |
| Container atau Kubernetes | Dokumentasi FastAPI menyarankan **satu proses per container** dan membiarkan orkestrator yang mereplikasi ([Container](container.md)) |
| Aplikasi menyimpan data di memori | Pindahkan ke basis data sebelum memakai banyak proses |
| Pekerjaan yang hanya menunggu I/O | Mulai dari satu proses dan ukur sebelum menambah |

Selain replikasi, dokumentasi FastAPI mencantumkan hal-hal lain yang harus diurus di produksi: HTTPS, menjalankan otomatis saat server hidup, memulai ulang bila mati, dan memori. `--workers` hanya sedikit membantu urusan memulai ulang; sisanya harus diatur di luar aplikasi.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Memakai `fastapi dev` atau `--reload` di produksi | Memakan sumber daya lebih banyak dan kurang stabil (dokumentasi FastAPI). |
| Menjalankan `--workers` dengan data di memori | Setiap proses punya data sendiri (teruji: `[1, 3, 8]`). |
| Mengira jumlah worker selalu lebih banyak lebih baik | Setiap proses memakai memori sendiri; ukur dulu. Tidak diukur di sini. |
| `--host 0.0.0.0` di komputer pribadi tanpa perlu | Membuka aplikasi ke jaringan. Pakai `127.0.0.1` untuk uji lokal. |
| Mengukur "CPU berat" dengan menunggu waktu | Hasil menyesatkan (teruji). Pakai jumlah langkah tetap. |
| Memakai Gunicorn di Windows | `ModuleNotFoundError: No module named 'fcntl'` (teruji). |
| Menggabungkan `--reload` dan `--workers` | Saling meniadakan menurut `--help`. |
| Menyerahkan HTTPS ke aplikasi | Biasanya ditangani proksi di depan aplikasi. Konfigurasi proksi dan HTTPS tidak diuji di sini. |
| Tidak mengatur `--forwarded-allow-ips` di belakang proksi | Alamat asli klien tidak terbaca benar. Tidak diuji. |

## Latihan

1. **Dasar.** Apa tiga perbedaan utama antara `fastapi dev` dan `fastapi run`?
2. **Prediksi.** Empat request CPU berat dikirim bersamaan ke server dengan empat proses pada mesin yang hanya punya satu inti. Apa yang kamu harapkan, dibanding mesin empat inti?
3. **Praktik.** Jalankan `fastapi run main.py --host 127.0.0.1 --port 8000 --workers 2`, lalu kirim `POST /kunjungan` berkali-kali. Bagaimana penghitungnya berperilaku?
4. **Analisis.** Mengapa menaruh daftar token yang dicabut di variabel Python bermasalah bila memakai `--workers`?

??? success "Kunci jawaban"
    Jawaban 3 dan 4 mengacu pada hasil uji di atas. Jawaban 1 mengacu pada tabel perbandingan, dan jawaban 2 adalah penalaran dari hasil pengukuran (tidak dijalankan pada mesin satu inti).

    1. `fastapi dev` memakai muat ulang otomatis (`--reload`) dan alamat `127.0.0.1`; `fastapi run` tanpa muat ulang, memiliki `--workers`, dan (menurut dokumentasi FastAPI) mendengarkan semua alamat (`0.0.0.0`).
    2. Keuntungannya hilang atau menyusut: empat proses tetap berbagi satu inti, jadi waktunya mendekati kasus satu proses. Percepatan dari `--workers` bergantung pada jumlah inti yang tersedia.
    3. Dengan dua proses, setiap proses memiliki penghitung sendiri. Total semua penghitung sama dengan jumlah request, tetapi tidak ada satu nilai yang menunjukkan jumlah keseluruhan (pada percobaan tiga proses: `[1, 3, 8]`, jumlahnya 12).
    4. Proses yang berbeda tidak berbagi memori. Token yang dicabut di satu proses tetap sah di proses lain, sehingga pencabutan tidak berlaku konsisten. Daftar itu harus disimpan di basis data atau penyimpanan bersama.

## Ringkasan

- `fastapi dev` untuk pengembangan; `fastapi run` untuk produksi, tanpa `--reload`.
- `fastapi run` memakai Uvicorn; `uvicorn main:app --workers N` juga bisa. Gunicorn tidak berjalan di Windows.
- `--workers` membuat beberapa proses, dan terbukti mempercepat pekerjaan CPU berat: 4,94 detik menjadi 1,33 detik untuk empat request bersamaan (pada mesin uji).
- Setiap proses punya memori sendiri; data bersama harus ada di luar memori proses.
- Pakai `127.0.0.1` untuk uji lokal; di produksi biasanya ada proksi yang menangani HTTPS di depan aplikasi.
- Di container, pertimbangkan satu proses per container.

## Langkah berikutnya

Lanjut ke [Container](container.md), atau kembali ke daftar materi di [Modul 10: Deployment](index.md).
