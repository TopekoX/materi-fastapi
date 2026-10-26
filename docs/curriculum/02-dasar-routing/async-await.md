# Dasar Async/Await

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan apa itu kode asinkron dan masalah yang diselesaikannya.
- [ ] Menjelaskan arti `async def`, `await`, dan coroutine.
- [ ] Memilih antara `def` dan `async def` untuk sebuah endpoint.
- [ ] Menjelaskan mengapa kode yang memblokir di dalam `async def` berbahaya.
- [ ] Membuktikan perbedaannya dengan pengukuran waktu.

## Prasyarat

- Sudah membaca [Endpoint Pertama](../01-pengenalan/endpoint-pertama.md), tempat `def` dan `async def` pertama kali disinggung.
- Fungsi dasar Python.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7** dan **FastAPI 0.162.0** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**. Angka waktu pada halaman ini berasal dari komputer uji saya dan akan sedikit berbeda di komputermu.

## Konsep: program yang menunggu

Banyak pekerjaan server berupa **menunggu**: menunggu basis data menjawab, menunggu layanan lain merespons, menunggu file dibaca. Selama menunggu, prosesor sebenarnya tidak sibuk.

Bayangkan seorang juru masak yang hanya mengerjakan satu hal sampai selesai: merebus air, lalu menunggu sampai mendidih sebelum menyentuh hal lain. Tamu yang lain mengantre. Juru masak yang lebih cerdik menaruh air di atas api, lalu mengerjakan hal lain **selama air dipanaskan**, dan kembali saat air siap.

Itulah ide **kode asinkron**: saat satu pekerjaan menunggu, program boleh mengerjakan pekerjaan lain. Dokumentasi FastAPI menyebut bahwa ini berbeda dengan paralelisme (mengerjakan banyak hal di saat yang sama); yang terjadi adalah bergantian secara cerdas ketika ada yang menunggu.

Python menyediakan dua kata kunci untuk ini:

| Kata kunci | Artinya |
|---|---|
| `async def` | Mendefinisikan fungsi yang boleh menunggu tanpa menahan program. Hasil pemanggilannya disebut **coroutine** |
| `await` | "Tunggu hasil ini, dan selama itu program boleh mengerjakan hal lain" |

## Bagian 1: async/await murni di Python

Sebelum FastAPI, lihat dulu cara kerjanya di Python biasa. Simpan sebagai `dasar_async.py`:

```python title="dasar_async.py"
--8<-- "fastapi/02-dasar-routing/async-await/dasar_async.py"
```

### Penjelasan kode

| Bagian | Fungsinya |
|---|---|
| `async def siapkan(nama)` | Fungsi asinkron yang "menyiapkan" sesuatu |
| `await asyncio.sleep(1)` | Menunggu 1 detik **tanpa menahan program**. Ini pengganti proses menunggu sungguhan, misalnya menunggu basis data |
| `satu_per_satu()` | Memanggil `await siapkan(...)` bergantian: yang kedua baru mulai setelah yang pertama selesai |
| `asyncio.gather(...)` | Menjalankan beberapa coroutine bersamaan dan menunggu semuanya selesai |
| `asyncio.run(...)` | Menjalankan coroutine dari kode biasa. Tanpa ini, fungsi `async def` tidak berjalan |

### Menjalankan

```bash
python dasar_async.py
```

Hasil dari eksekusi nyata:

```text
nasi siap
sayur siap
teh siap
satu per satu: 3.01 detik
['nasi siap', 'sayur siap', 'teh siap']
bersamaan: 1.00 detik
```

Tiga pekerjaan yang masing-masing menunggu 1 detik memakan 3 detik jika bergantian, tetapi hanya sekitar 1 detik jika menunggunya dilakukan bersamaan. Ini manfaat asinkron: **menghemat waktu menunggu**, bukan mempercepat pekerjaan yang benar-benar menghitung.

### Dua kesalahan pemula di Python

**Lupa `await`.** Memanggil fungsi `async def` tanpa `await` tidak menjalankannya, melainkan menghasilkan objek coroutine. Pada pengujian, `print(f())` untuk `async def f()` menampilkan:

```text
RuntimeWarning: coroutine 'f' was never awaited
<coroutine object f at 0x...>
```

**`await` di fungsi biasa.** Menulis `await` di dalam `def` biasa menghasilkan galat pada pengujian:

```text
SyntaxError: 'await' outside async function
```

Dokumentasi resmi FastAPI juga menyatakan bahwa `await` hanya bisa dipakai di dalam fungsi `async def`.

## Bagian 2: async dan def di FastAPI

Di FastAPI, kamu boleh menulis endpoint dengan `def` atau `async def`. Dokumentasi resmi memberi aturan berikut:

| Situasi | Pakai |
|---|---|
| Library yang kamu pakai harus dipanggil dengan `await` | `async def` |
| Library berkomunikasi dengan sesuatu (basis data, API, file) tetapi **tidak** mendukung `await` | `def` biasa |
| Aplikasi tidak perlu berkomunikasi dan menunggu apa pun | `async def` |
| Tidak yakin | `def` biasa |

Dokumentasi juga menyatakan bahwa kamu boleh mencampur keduanya, dan bahwa fungsi `def` biasa dijalankan FastAPI di *threadpool* terpisah agar tidak memblokir server.

Berikut pembuktiannya. Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/02-dasar-routing/async-await/main.py"
```

### Penjelasan kode

| Endpoint | Jenis | Cara menunggu |
|---|---|---|
| `/def-menunggu` | `def` biasa | `time.sleep(1)`: menunggu yang **memblokir** |
| `/async-menunggu` | `async def` | `await asyncio.sleep(1)`: menunggu yang **tidak memblokir** |
| `/async-memblokir` | `async def` | `time.sleep(1)`: menunggu yang memblokir **di dalam** fungsi asinkron |

Ketiganya sama-sama "menunggu 1 detik" dan mengembalikan JSON kecil. `time.sleep` adalah contoh kode yang memblokir, yaitu menahan seluruh program selama menunggu. `asyncio.sleep` dipakai dengan `await`, sehingga program bisa mengerjakan hal lain selama menunggu.

### Skrip pengukur

Skrip ini mengirim tiga request **bersamaan** ke setiap endpoint dan mengukur total waktunya. Simpan sebagai `uji_paralel.py`:

```python title="uji_paralel.py"
--8<-- "fastapi/02-dasar-routing/async-await/uji_paralel.py"
```

| Bagian | Fungsinya |
|---|---|
| `httpx.AsyncClient` | Klien HTTP asinkron. Pada pengujian, `httpx` ikut terpasang bersama `fastapi[standard]` |
| `asyncio.gather(*[klien.get(path) for _ in range(JUMLAH)])` | Mengirim `JUMLAH` request sekaligus |
| `time.perf_counter()` | Pengukur waktu untuk menghitung total durasi |

## Menjalankan dan mengukur

Terminal 1, jalankan server:

```bash
fastapi dev main.py
```

Terminal 2, jalankan pengukur (alamat bawaan `http://127.0.0.1:8000`, atau berikan alamat lain sebagai argumen):

```bash
python uji_paralel.py
```

### Satu request

Dengan `curl`, ketiga endpoint menjawab `200 OK` dalam sekitar 1 detik (pada pengujian 1.09, 1.04, dan 1.03 detik), dengan body seperti:

```json
{"jenis":"async def, await asyncio.sleep(1)"}
```

Untuk **satu** request, ketiganya sama saja. Perbedaan baru terlihat saat ada banyak request bersamaan.

### Tiga request bersamaan

Dua kali putaran pengukuran, semua status `200`:

| Endpoint | Putaran 1 | Putaran 2 |
|---|---|---|
| `/def-menunggu` | 1.04 detik | 1.03 detik |
| `/async-menunggu` | 1.01 detik | 1.01 detik |
| `/async-memblokir` | **3.01 detik** | **3.01 detik** |

Cara membacanya:

- `/def-menunggu` dan `/async-menunggu` selesai dalam sekitar 1 detik: tiga request menunggu bersamaan.
- `/async-memblokir` memakan sekitar 3 detik: `time.sleep` di dalam `async def` menahan seluruh server, sehingga request diproses satu per satu.
- Endpoint `def` biasa **tidak** bermasalah walau memakai `time.sleep`, karena FastAPI menjalankannya di threadpool, seperti dijelaskan dokumentasi resmi.

### Dampak ke endpoint lain

Kode yang memblokir tidak hanya memperlambat dirinya sendiri, tetapi juga **request lain**. Pada pengujian, `/async-menunggu` seharusnya selesai dalam 1 detik:

| Kondisi | Waktu `/async-menunggu` |
|---|---|
| Saat `/def-menunggu` sedang berjalan | 1.02 detik |
| Saat `/async-memblokir` sedang berjalan | 1.94 detik |

Request kedua harus ikut menunggu sampai blokirnya selesai.

## Aturan praktis

1. Jika kamu memakai library yang dokumentasinya meminta `await`, tulis `async def`.
2. Jika library tidak mendukung `await` (menurut dokumentasi resmi, ini berlaku untuk sebagian besar library basis data), tulis `def` biasa.
3. **Jangan** memanggil kode yang memblokir (seperti `time.sleep` atau library biasa yang menunggu) di dalam `async def`.
4. Tidak yakin? Pakai `def` biasa, sesuai saran dokumentasi resmi.

Untuk materi ini, sebagian besar endpoint cukup ditulis dengan `def`. Pada modul basis data, aturan ini akan dipakai ketika memilih library.

## Kesalahan umum

Semua kasus berikut dijalankan dan dicatat apa adanya.

### 1. Memakai kode yang memblokir di `async def`

Gejala: waktu respons memanjang saat banyak request, seperti `/async-memblokir` (3.01 detik untuk tiga request). **Solusi:** ganti dengan padanan yang bisa di-`await` (misalnya `await asyncio.sleep(...)`), atau ubah fungsinya menjadi `def` biasa.

### 2. Menulis `await` di dalam `def`

Hasilnya `SyntaxError: 'await' outside async function` saat file dijalankan atau diimpor. **Solusi:** ubah fungsinya menjadi `async def`.

### 3. Lupa `await`

Pemanggilan fungsi asinkron tanpa `await` menghasilkan coroutine, bukan hasil kerjanya, disertai `RuntimeWarning: coroutine ... was never awaited`. **Solusi:** tambahkan `await` di depan pemanggilan.

### 4. Mengira `async def` otomatis lebih cepat

Untuk satu request, `/def-menunggu` (1.09 detik) dan `/async-menunggu` (1.04 detik) praktis sama. Manfaat asinkron muncul ketika **banyak request menunggu bersamaan**, bukan untuk satu request, dan tidak mempercepat pekerjaan yang murni menghitung.

## Latihan

1. **Dasar.** Ubah `dasar_async.py` agar menyiapkan empat item (tambahkan `lauk`). Prediksikan waktu `satu_per_satu` dan `bersamaan`, lalu jalankan.
2. **Menengah.** Perbaiki `/async-memblokir` agar tiga request bersamaan selesai dalam sekitar 1 detik, dengan tetap memakai `async def`.
3. **Menengah.** Perbaiki `/async-memblokir` dengan cara lain, yaitu tanpa mengubah `time.sleep(1)`.
4. **Tantangan.** Kamu akan memakai library basis data yang **tidak** mendukung `await`. Pilih `def` atau `async def`, dan jelaskan alasannya berdasarkan dokumentasi resmi.

??? success "Kunci jawaban"
    1. Prediksi: sekitar 4 detik dan 1 detik. Hasil yang teramati pada pengujian: `satu per satu: 4.03 detik` dan `bersamaan: 1.01 detik`.
    2. Ganti `time.sleep(1)` dengan `await asyncio.sleep(1)`. Kodenya sama dengan `/async-menunggu`, yang pada pengujian selesai dalam sekitar 1 detik untuk tiga request bersamaan.
    3. Ubah `async def` menjadi `def` biasa. Kodenya sama dengan `/def-menunggu`, yang pada pengujian juga selesai dalam sekitar 1 detik.
    4. Pilih `def` biasa. Dokumentasi resmi menyatakan bahwa library yang berkomunikasi dengan sesuatu tetapi tidak mendukung `await` ditulis dengan `def`; FastAPI akan menjalankannya di threadpool agar tidak memblokir server.

    Jawaban 2 dan 3 merujuk pada kode yang identik dengan endpoint yang telah diukur; versi yang dimodifikasi itu sendiri tidak saya jalankan terpisah.

## Ringkasan

- Kode asinkron memanfaatkan waktu menunggu untuk mengerjakan hal lain. Ia menghemat waktu menunggu, bukan mempercepat perhitungan.
- `async def` membuat coroutine, dan `await` menunggu hasilnya. `await` hanya bisa dipakai di dalam `async def`.
- Lupa `await` menghasilkan coroutine yang tidak berjalan.
- Di FastAPI: `async def` untuk library yang memakai `await`, `def` biasa untuk yang tidak, dan `def` bila ragu.
- Fungsi `def` biasa dijalankan di threadpool, sehingga aman memakai kode yang memblokir.
- Kode yang memblokir di dalam `async def` menahan seluruh server: pada pengukuran, tiga request bersamaan memakan 3.01 detik, bukan 1 detik, dan memperlambat request lain.

## Langkah berikutnya

Kerjakan [Latihan Gabungan: Katalog Buku](latihan-gabungan.md) untuk menggabungkan seluruh materi Modul 02, lalu lanjut ke [Modul 03: Data dan Validasi](../03-data-validasi/index.md). Penerapan async/await pada basis data dibahas di [Modul 06](../06-basis-data/index.md).
