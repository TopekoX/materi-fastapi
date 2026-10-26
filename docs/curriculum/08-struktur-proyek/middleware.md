# Middleware

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan apa itu middleware dan di mana posisinya dalam alur request.
- [ ] Menulis middleware dengan `@app.middleware("http")` dan `call_next`.
- [ ] Menambahkan header ke response dan menyimpan data per request lewat `request.state`.
- [ ] Menjawab langsung dari middleware tanpa memanggil endpoint.
- [ ] Menjelaskan urutan eksekusi beberapa middleware.
- [ ] Mengenali apa yang tidak dijangkau middleware saat terjadi exception yang tak tertangani.
- [ ] Memasang middleware bawaan: `GZipMiddleware` dan `TrustedHostMiddleware`.

## Prasyarat

- Sudah membaca [Konfigurasi dan Environment](konfigurasi-environment.md) dan [Router Modular](router-modular.md).
- Sudah membaca [CORS](../07-autentikasi-keamanan/cors.md): `CORSMiddleware` yang kamu pasang di sana adalah sebuah middleware.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7** dan **FastAPI 0.162.0** (dengan Starlette 1.10.0) di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

**Middleware** adalah fungsi yang membungkus seluruh aplikasi. Menurut dokumentasi FastAPI, ia berjalan pada setiap **request** sebelum diproses oleh endpoint mana pun, dan pada setiap **response** sebelum dikembalikan. Ia bisa memeriksa atau mengubah request, menjalankan kode, meneruskan request, lalu memeriksa atau mengubah response.

Gunakan middleware untuk hal yang berlaku untuk **semua** endpoint: mengukur waktu, memberi pengenal pada setiap request, menambah header, atau menolak semua request pada kondisi tertentu (misalnya mode pemeliharaan). Untuk logika yang hanya relevan bagi sebagian endpoint, gunakan [dependency](../05-dependency-injection/konsep-dependency.md), bukan middleware.

```mermaid
flowchart LR
    K[Klien] --> M1[Middleware luar] --> M2[Middleware dalam] --> E[Endpoint]
    E --> M2 --> M1 --> K
```

Sebuah middleware punya dua bagian:

```python
async def contoh(request: Request, call_next):
    # 1. kode SEBELUM endpoint (mengurus request)
    response = await call_next(request)   # 2. meneruskan ke bagian berikutnya
    # 3. kode SESUDAH endpoint (mengurus response)
    return response
```

`call_next` meneruskan request ke langkah berikutnya (middleware lain atau endpoint) dan mengembalikan response yang dihasilkan.

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/08-struktur-proyek/middleware/main.py"
```

## Penjelasan kode

### Mengukur waktu proses

```python
@app.middleware("http")
async def waktu_proses(request: Request, call_next):
    catat(request, "waktu: masuk")
    mulai = time.perf_counter()
    response = await call_next(request)
    durasi_ms = (time.perf_counter() - mulai) * 1000
    response.headers["X-Waktu-Proses"] = f"{durasi_ms:.1f} ms"
    catat(request, "waktu: keluar")
    return response
```

- `@app.middleware("http")` mendaftarkan fungsi sebagai middleware untuk request HTTP. Fungsi harus `async`.
- Waktu mulai dicatat sebelum `call_next`, dan durasi dihitung sesudahnya. Dokumentasi FastAPI memakai `time.perf_counter()` karena lebih tepat untuk mengukur durasi daripada `time.time()`.
- Header ditambahkan pada `response`. Nama header kustom lazimnya berawalan `X-`.
- `catat` hanya alat percobaan yang mencatat urutan pemanggilan untuk path `/halo`.

### Pengenal per request dan `request.state`

```python
request.state.request_id = uuid.uuid4().hex[:8]
response = await call_next(request)
response.headers["X-Request-ID"] = request.state.request_id
```

`request.state` adalah tempat menyimpan data untuk **satu request**. Nilai yang diisi di middleware bisa dibaca oleh endpoint dengan parameter `request: Request` (lihat endpoint `/id`). Pengenal seperti ini berguna untuk mencocokkan baris log dengan satu request.

### Menjawab tanpa memanggil endpoint

```python
@app.middleware("http")
async def pemeliharaan(request: Request, call_next):
    if status_pemeliharaan["aktif"] and not request.url.path.startswith("/pemeliharaan"):
        return JSONResponse(status_code=503, content={"detail": "Sedang dalam pemeliharaan"})
    response = await call_next(request)
    return response
```

Middleware boleh **tidak memanggil** `call_next` dan langsung mengembalikan response. Di sini, saat mode pemeliharaan aktif, semua request (kecuali ke `/pemeliharaan/...`, agar mode bisa dimatikan lagi) dijawab `503` dan endpoint tidak dijalankan. `503` berarti layanan sementara tidak tersedia.

### Urutan beberapa middleware

Middleware yang didaftarkan **pertama** berada paling **dalam** (dekat endpoint), dan yang didaftarkan **terakhir** paling **luar** (menerima request lebih dulu). Menurut dokumentasi FastAPI: yang terakhir ditambahkan adalah yang terluar. Pada contoh: `waktu_proses` paling dalam, lalu `id_permintaan`, lalu `pemeliharaan` paling luar.

## Menjalankan

```powershell
fastapi dev main.py
```

Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah.

## Mencoba request

Hasil di bawah dijalankan dengan `curl.exe` (`-i` menampilkan header).

### Header dari middleware

```powershell
curl.exe -i http://127.0.0.1:8000/halo
```

```text
HTTP/1.1 200 OK
x-waktu-proses: 1.4 ms
x-request-id: 5c956847
{"pesan":"Halo"}
```

Dua header muncul pada response yang endpoint-nya tidak pernah menyebutnya. Nilai waktu dan pengenal berbeda setiap request.

`GET /id` mengembalikan `{"request_id":"b142fe66"}`, dan header `x-request-id` pada response yang sama bernilai sama: endpoint membaca nilai yang diisi middleware lewat `request.state`.

### Urutan eksekusi

Setelah satu request ke `/halo`, `GET /jejak` menampilkan:

```json
["pemeliharaan: masuk","id: masuk","waktu: masuk","endpoint","waktu: keluar","id: keluar","pemeliharaan: keluar"]
```

Pada jalan masuk: yang **terluar** (`pemeliharaan`) lebih dulu, lalu `id`, lalu `waktu`, lalu endpoint. Pada jalan keluar, urutannya dibalik.

### Response error dan middleware

| Request | Status | Header `x-waktu-proses` dan `x-request-id` |
|---|---|---|
| `GET /gagal-http` (`HTTPException` 418) | `418` | ada |
| `GET /tidak-ada` | `404` | ada |
| `GET /rusak` (`ZeroDivisionError`, tidak tertangani) | `500` | **tidak ada** |

`HTTPException` dan `404` diubah FastAPI menjadi response biasa sebelum sampai ke middleware, sehingga header tetap ditambahkan. Exception yang tidak tertangani menembus middleware, dan jawaban `500` datang tanpa header dari middleware (penjelasan penyebabnya, yaitu lapisan yang lebih luar yang menjawabnya, adalah penalaran; yang teruji hanyalah header yang tidak ada). Karena itu, jangan mengandalkan middleware untuk **selalu** menambah header atau mencatat akhir request. Untuk menangani exception, pakai exception handler (lihat [Handler Error Kustom](../04-penanganan-error/handler-kustom.md)).

### Menjawab tanpa memanggil endpoint

| Request | Status | Isi |
|---|---|---|
| `POST /pemeliharaan/on` | `200` | `{"aktif":true}` |
| `GET /halo` | `503` | `{"detail":"Sedang dalam pemeliharaan"}`, **tanpa** header `x-` |
| `GET /jejak` | `503` | pesan yang sama |
| `POST /pemeliharaan/off` | `200` | `{"aktif":false}` |
| `GET /halo` | `200` | `{"pesan":"Halo"}` |

Pada `503`, header `x-waktu-proses` dan `x-request-id` tidak ada, karena `pemeliharaan` adalah middleware terluar dan menjawab sebelum request sampai ke dua middleware dalam. Ini konsekuensi urutan di atas. (`/jejak` ikut diblokir karena path-nya bukan `/pemeliharaan/...`.)

### Middleware bawaan: `GZipMiddleware` dan `TrustedHostMiddleware`

Selain menulis sendiri, kamu bisa memasang middleware siap pakai dengan `app.add_middleware(Kelas, ...)`. Dua yang berguna, di `main_bawaan.py`:

```python title="main_bawaan.py"
--8<-- "fastapi/08-struktur-proyek/middleware/main_bawaan.py"
```

- `GZipMiddleware(minimum_size=500)` mengompres response yang lebih besar dari 500 byte, **bila klien menyatakan mendukung gzip** lewat header `Accept-Encoding`.
- `TrustedHostMiddleware(allowed_hosts=[...])` hanya menerima request yang header `Host`-nya ada di daftar, sebagai perlindungan terhadap header `Host` palsu.

Hasil `curl.exe` (`--raw` agar isi tidak didekompresi otomatis):

| Request | Status | Header dan ukuran |
|---|---|---|
| `GET /besar` tanpa `Accept-Encoding` | `200` | `content-length: 5300`, tanpa `content-encoding` |
| `GET /besar` dengan `Accept-Encoding: gzip` | `200` | `content-length: 695`, `content-encoding: gzip` |
| `GET /kecil` dengan `Accept-Encoding: gzip` | `200` | `content-length: 19`, tanpa `content-encoding` (di bawah 500 byte) |
| `GET /kecil` dengan `Host: localhost:8932` | `200` | diterima |
| `GET /kecil` dengan `Host: jahat.example.com` | `400` | `Invalid host header` |

Isi besar mengecil dari 5300 byte menjadi 695 byte. Dengan `curl --compressed`, isinya didekompresi dan terbaca normal (`{"data":["tugas nomor 0",...`).

`HTTPSRedirectMiddleware` (mengalihkan HTTP ke HTTPS) juga tersedia di `fastapi.middleware.httpsredirect`, tetapi **tidak diuji** di sini karena membutuhkan HTTPS, yang dibahas di [Modul 10](../10-deployment/index.md). Pemasangannya mengikuti pola yang sama.

### Dokumentasi otomatis

Middleware tidak muncul di `/openapi.json`. Tampilan Swagger UI **belum diverifikasi** lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Lupa `return response` | Middleware tidak mengembalikan apa pun dan request gagal. Tidak dijalankan di sini. |
| Lupa `await call_next(request)` | Endpoint tidak pernah dipanggil. Tidak diuji. |
| Mengharapkan header ada di setiap response | Pada exception tak tertangani, header tidak ada (teruji: `500`). |
| Salah mengira urutan | Yang didaftarkan terakhir adalah yang terluar (teruji lewat `jejak`). |
| Memakai middleware untuk logika yang hanya milik sebagian endpoint | Mubazir. Pakai dependency atau router dengan `dependencies`. |
| Pekerjaan berat di middleware | Memperlambat semua request. Untuk pekerjaan setelah response, lihat halaman berikutnya. |
| Menjawab `503` tanpa jalan untuk mematikan mode | Aplikasi terkunci. Pada contoh, `/pemeliharaan/...` dikecualikan. |
| Memasang middleware bawaan yang salah urutan | Contohnya `CORSMiddleware` yang terluar dan middleware lain menjawab sebelum header CORS ditambahkan. Tidak diuji di sini. |

## Latihan

1. **Dasar.** Apa yang dilakukan `call_next`?
2. **Praktik.** Tambahkan middleware yang menambah header `X-Versi-API: v1` pada setiap response. Di mana ia ditaruh relatif terhadap yang lain bila header itu harus ikut ditambahkan juga pada response `503` mode pemeliharaan?
3. **Prediksi.** Urutan `jejak` bila `pemeliharaan` didaftarkan lebih dulu (paling atas) daripada `waktu_proses`?
4. **Analisis.** Mengapa `GET /rusak` tidak mendapat header `x-request-id`, sedangkan `GET /gagal-http` mendapatnya?

??? success "Kunci jawaban"
    Jawaban 4 mengacu pada hasil uji di atas. Jawaban 1 sampai 3 adalah penalaran dari dokumentasi FastAPI dan hasil uji urutan; jawaban 2 dan 3 tidak dijalankan.

    1. `call_next` meneruskan request ke langkah berikutnya (middleware lain atau endpoint) dan mengembalikan response yang dihasilkan. Kode sebelum pemanggilannya mengurus request, dan kode sesudahnya mengurus response.
    2. Didaftarkan **paling akhir** (terluar), agar ia membungkus semuanya, termasuk jawaban `503` dari `pemeliharaan`:

        ```python
        @app.middleware("http")
        async def versi_api(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Versi-API"] = "v1"
            return response
        ```

    3. Urutannya terbalik: yang didaftarkan pertama menjadi terdalam. `pemeliharaan` kini paling dalam, sehingga `waktu_proses` dan `id_permintaan` lebih dulu menerima request.
    4. `HTTPException` diubah menjadi response biasa sebelum sampai ke middleware, jadi middleware menambahkan header. Exception tak tertangani menembus middleware dan dijawab `500` oleh lapisan lebih luar, sehingga header tidak sempat ditambahkan.

## Ringkasan

- Middleware membungkus semua endpoint: ia berjalan pada setiap request sebelum endpoint dan pada setiap response sebelum dikirim.
- Tulis dengan `@app.middleware("http")`, `request`, dan `await call_next(request)`; selalu `return response`.
- Gunakan `request.state` untuk menyimpan data per request, dan `response.headers` untuk menambah header.
- Middleware boleh menjawab langsung tanpa memanggil `call_next`.
- Yang didaftarkan terakhir adalah yang terluar.
- Exception yang tak tertangani menembus middleware; headernya tidak ditambahkan pada `500`.
- Middleware bawaan dipasang dengan `app.add_middleware`: `GZipMiddleware` mengompres response besar bila klien mendukung gzip, dan `TrustedHostMiddleware` menolak header `Host` yang tidak terdaftar.

## Langkah berikutnya

Lanjut ke [Background Task](background-task.md), atau kembali ke daftar materi di [Modul 08: Struktur Proyek](index.md).
