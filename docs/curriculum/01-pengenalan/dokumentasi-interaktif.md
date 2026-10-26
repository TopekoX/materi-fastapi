# Dokumentasi Interaktif Otomatis

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan apa itu dokumentasi interaktif otomatis dan dari mana ia berasal.
- [ ] Membuka dan membedakan `/docs`, `/redoc`, dan `/openapi.json`.
- [ ] Memengaruhi isi dokumentasi lewat `summary`, `tags`, dan docstring.
- [ ] Mengubah atau mematikan alamat dokumentasi.
- [ ] Mengenali batasan dokumentasi ini, termasuk kebutuhan akan internet.

## Prasyarat

- Sudah membaca [Menjalankan Server](menjalankan-server.md) dan [Aplikasi Pertama](aplikasi-pertama.md).
- Pengertian OpenAPI dan Swagger UI sudah diperkenalkan di [Apa itu FastAPI](apa-itu-fastapi.md#dokumentasi-interaktif-otomatis); halaman ini tidak mengulanginya.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7** dan **FastAPI 0.162.0** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Bayangkan restoran. Kamu butuh **daftar menu** agar tahu apa yang bisa dipesan, dan **cara memesan**. Untuk API, "menu" itu adalah daftar endpoint beserta method dan format datanya.

Biasanya dokumentasi ini ditulis tangan dan mudah ketinggalan saat kode berubah. FastAPI mengatasinya dengan membuat dokumentasi **dari kodemu sendiri**. Alurnya:

1. FastAPI membaca endpoint yang kamu daftarkan.
2. Hasilnya disusun menjadi deskripsi OpenAPI dalam format JSON, di alamat `/openapi.json`.
3. Dua halaman web membaca deskripsi itu dan menampilkannya: **Swagger UI** di `/docs` dan **ReDoc** di `/redoc`.

Karena sumbernya kode, dokumentasi selalu sesuai dengan aplikasi yang sedang berjalan. Swagger UI juga bersifat interaktif: selain dibaca, endpoint bisa dicoba langsung dari halamannya.

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/01-pengenalan/dokumentasi-interaktif/main.py"
```

## Penjelasan kode

### Metadata aplikasi

```python
app = FastAPI(
    title="Belajar FastAPI",
    description="Contoh dokumentasi interaktif otomatis.",
    version="0.1.0",
)
```

Sama seperti di [Aplikasi Pertama](aplikasi-pertama.md#membuat-aplikasi-dengan-metadata): ketiga isian ini tampil di bagian atas dokumentasi.

### Tambahan pada decorator

```python
@app.get("/", summary="Halaman utama", tags=["Umum"])
```

| Parameter | Fungsinya |
|---|---|
| `summary` | Judul singkat endpoint di dokumentasi. Jika tidak diisi, FastAPI menurunkannya dari nama fungsi (seperti "Halaman Utama" untuk `halaman_utama`, lihat [Endpoint Pertama](endpoint-pertama.md)) |
| `tags` | Daftar label untuk mengelompokkan endpoint. Pada kode ini ada dua kelompok: `Umum` dan `Tugas` |

### Docstring

```python
def halaman_utama():
    """Mengembalikan pesan sambutan."""
    return {"pesan": "Halo dari dokumentasi interaktif!"}
```

Teks di antara tiga tanda kutip di awal fungsi disebut *docstring*. FastAPI memakainya sebagai **deskripsi** endpoint. Pada pengujian, isi docstring muncul sebagai bidang `description` di `/openapi.json`.

### Endpoint dengan status code

```python
@app.post("/tugas", status_code=201, summary="Buat tugas", tags=["Tugas"])
```

Parameter `status_code=201` (dikenalkan di [HTTP dan REST](http-dan-rest.md)) ikut tercatat di dokumentasi: pada pengujian, daftar response endpoint ini berisi `201`, bukan `200`.

## Menjalankan dan membuka dokumentasi

Jalankan seperti biasa dari folder `main.py` (lihat [Menjalankan Server](menjalankan-server.md)):

```bash
fastapi dev main.py
```

Pada pengujian dengan port 8790, ketiga alamat berikut menjawab `200`:

| Alamat | Isi | Tipe konten |
|---|---|---|
| `/docs` | Swagger UI | `text/html` |
| `/redoc` | ReDoc | `text/html` |
| `/openapi.json` | Deskripsi OpenAPI mentah | `application/json` |

Judul halaman pada pengujian: `Belajar FastAPI - Swagger UI` dan `Belajar FastAPI - ReDoc`, yaitu `title` yang kamu tulis.

!!! warning "Butuh internet"
    Halaman `/docs` memuat tampilan Swagger UI dari `cdn.jsdelivr.net` (paket `swagger-ui-dist@5`), dan `/redoc` memuat ReDoc dari sana juga (`redoc@2`). Pada pengujian, halaman-halaman ini juga merujuk ke `fonts.googleapis.com` dan `fastapi.tiangolo.com`. Server mengirim halaman HTML-nya tanpa masalah, tetapi **tampilan di browser belum saya lihat langsung**, begitu pula perilakunya saat tanpa internet.

## Membaca `/openapi.json`

Ini bahan mentah yang dipakai kedua halaman tadi. Ringkasan isinya pada pengujian (disusun dari hasil nyata):

| Path | Method | Tag | Summary | Response |
|---|---|---|---|---|
| `/` | `get` | `Umum` | Halaman utama | `200` |
| `/kesehatan` | `get` | `Umum` | Cek kesehatan | `200` |
| `/tugas` | `post` | `Tugas` | Buat tugas | `201` |

Bidang `description` tiap endpoint berisi docstring-nya. Pada tingkat atas, berkas ini berisi bagian `info`, `openapi`, dan `paths`.

## Mencoba endpoint dari Swagger UI

Langkah umumnya di `/docs`:

1. Klik salah satu endpoint untuk membukanya.
2. Klik tombol **Try it out**, lalu **Execute**.
3. Swagger UI menampilkan request yang dikirim dan response dari servermu.

Langkah ini **belum saya lakukan secara visual**. Sebagai gantinya, saya mengirim request yang setara lewat `curl`, dan hasilnya adalah yang akan kamu lihat sebagai response:

| Request setara | Status | Body |
|---|---|---|
| `GET /` | `200 OK` | `{"pesan":"Halo dari dokumentasi interaktif!"}` |
| `GET /kesehatan` | `200 OK` | `{"status":"ok"}` |
| `POST /tugas` | `201 Created` | `{"aksi":"membuat tugas baru"}` |

Bandingkan hasil `POST /tugas` di atas dengan [HTTP dan REST](http-dan-rest.md): bedanya hanya isi pesan, status `201` sama.

## Mengatur alamat dokumentasi

Alamat bawaan bisa diubah atau dimatikan lewat parameter `FastAPI(...)`. Hasil pengujian (status code tiap alamat):

| Pengaturan | `/docs` | `/redoc` | `/openapi.json` |
|---|---|---|---|
| Bawaan | 200 | 200 | 200 |
| `docs_url="/dokumentasi"` | 404 (pindah ke `/dokumentasi`: 200) | 200 | 200 |
| `docs_url=None` | 404 | 200 | 200 |
| `redoc_url=None` | 200 | 404 | 200 |
| `docs_url=None, redoc_url=None` | 404 | 404 | 200 |
| `openapi_url=None` | 404 | 404 | 404 |
| `openapi_url="/skema.json"` | 200 | 200 | 404 (pindah ke `/skema.json`: 200) |

Hal yang perlu dicatat: mematikan `openapi_url` otomatis mematikan `/docs` dan `/redoc` juga, karena kedua halaman itu bergantung pada berkas tersebut.

Contoh penggunaannya:

```python
app = FastAPI(docs_url="/dokumentasi", redoc_url=None)
```

!!! note "Soal keamanan"
    Dokumentasi otomatis membuka daftar semua endpoint-mu kepada siapa pun yang bisa menjangkau server. Itu nyaman saat belajar. Untuk aplikasi nyata, pertimbangkan apakah dokumentasi perlu dimatikan atau dibatasi; hal itu dibahas di modul keamanan dan deployment.

## Kesalahan umum

Semua kasus berikut dijalankan dan dicatat apa adanya.

### 1. `/docs` menghasilkan 404

Penyebabnya bisa `docs_url` diganti atau dimatikan, atau `openapi_url=None` (lihat tabel di atas). Pada pengujian, `GET /docs` mengembalikan `404` pada ketiga kasus tersebut. **Solusi:** periksa argumen `FastAPI(...)` di kodemu, atau buka alamat baru yang kamu tetapkan.

### 2. Alamat dokumentasi benar, tetapi tampilan kosong

Halaman dokumentasi bergantung pada berkas dari CDN. Jika koneksi internet bermasalah, tampilan bisa tidak muncul. Kasus ini **belum saya reproduksi**, jadi anggap sebagai kemungkinan, bukan hasil uji. **Solusi:** periksa koneksi, atau tetap gunakan `/openapi.json` yang dilayani langsung oleh servermu.

### 3. Mencoba `POST` dari address bar browser

Mengetik alamat di address bar mengirim `GET`. Untuk `POST`, pakai tombol **Try it out** di `/docs` atau `curl -X POST`. Pada pengujian, `POST /tugas` lewat `curl` mengembalikan `201 Created`.

### 4. Perubahan kode tidak muncul di dokumentasi

Dokumentasi dibuat dari kode yang sedang berjalan. Jika server belum memuat kode terbarumu, dokumentasi tetap versi lama. **Solusi:** pastikan hanya ada satu server di port itu dan restart bila perlu (lihat [Menjalankan Server](menjalankan-server.md#kesalahan-umum)).

## Latihan

1. **Dasar.** Jalankan `main.py`, buka `/docs`, lalu sebutkan dua kelompok tag yang ada dan endpoint di masing-masing.
2. **Menengah.** Tambahkan endpoint `GET /versi` dengan `summary` dan docstring buatanmu sendiri. Periksa `/openapi.json` dan pastikan `summary` serta `description` muncul.
3. **Menengah.** Pindahkan Swagger UI ke `/dokumentasi` dengan `docs_url="/dokumentasi"`, lalu pastikan `/docs` menjadi `404`.
4. **Tantangan.** Matikan `/docs` dan `/redoc` tetapi pertahankan `/openapi.json`. Setelah itu, jelaskan apa yang terjadi bila `openapi_url=None` ikut diisi.

??? success "Petunjuk jawaban"
    1. Tag `Umum`: `/` dan `/kesehatan`. Tag `Tugas`: `POST /tugas`.
    2. Mekanisme `summary` dan docstring sama dengan yang teruji pada tiga endpoint di atas; contoh `/versi` buatanmu sendiri tidak saya jalankan.
    3. Pada pengujian, `docs_url="/dokumentasi"` menghasilkan `/dokumentasi` `200` dan `/docs` `404`.
    4. Gunakan `FastAPI(docs_url=None, redoc_url=None)`. Pada pengujian, hasilnya `/openapi.json` tetap `200`. Bila `openapi_url=None` diisi, ketiganya (`/docs`, `/redoc`, `/openapi.json`) menjadi `404`.

## Ringkasan

- FastAPI membuat dokumentasi API dari kodemu: deskripsi OpenAPI di `/openapi.json`, ditampilkan oleh Swagger UI (`/docs`) dan ReDoc (`/redoc`).
- `summary`, `tags`, dan docstring pada endpoint memperkaya dokumentasi. `status_code` ikut tercatat.
- Alamat dokumentasi bisa diubah atau dimatikan dengan `docs_url`, `redoc_url`, dan `openapi_url`; mematikan `openapi_url` mematikan semuanya.
- Halaman `/docs` dan `/redoc` memuat berkas dari CDN sehingga butuh internet; tampilan visualnya belum diverifikasi di materi ini.
- Dokumentasi membuka daftar endpoint-mu, jadi pertimbangkan keamanannya pada aplikasi nyata.

## Langkah berikutnya

Lanjutkan ke [Endpoint Pertama](endpoint-pertama.md), atau kembali ke [Modul 01: Pengenalan](index.md).
