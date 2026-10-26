# Latihan Gabungan: Katalog Buku

## Tujuan pembelajaran

Setelah mengerjakan latihan ini, kamu mampu:

- [ ] Menggabungkan path parameter, query parameter, dan urutan route dalam satu aplikasi.
- [ ] Memilih `def` atau `async def` untuk tiap endpoint.
- [ ] Menguji aplikasi sendiri dan membaca hasilnya, termasuk error `422`.
- [ ] Mengenali keterbatasan aplikasi yang kamu buat.

## Prasyarat

Keempat materi di Modul 02:

- [Path Parameter](path-parameter.md)
- [Query Parameter](query-parameter.md)
- [Urutan Route](urutan-route.md)
- [Dasar Async/Await](async-await.md)

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7** dan **FastAPI 0.162.0** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Skenario

Kamu diminta membuat API kecil untuk **katalog buku**. Datanya disimpan di memori (sebuah list), karena penyimpanan sungguhan baru dibahas di Modul 06. Berikut data yang dipakai:

| id | Judul | Penulis | Tahun |
|---|---|---|---|
| 1 | Belajar Python Dasar | Sari Dewi | 2019 |
| 2 | Memahami HTTP | Budi Santoso | 2021 |
| 3 | FastAPI untuk Pemula | Sari Dewi | 2023 |
| 4 | Dasar Basis Data | Rahmat Hidayat | 2018 |

Judul dan nama penulis di atas fiktif, hanya untuk latihan.

## Spesifikasi

Aplikasi bernama `Katalog Buku` versi `0.1.0` dengan empat endpoint:

| Endpoint | Fungsinya | Parameter |
|---|---|---|
| `GET /status` | Menampilkan status dan jumlah buku | Tidak ada |
| `GET /buku` | Daftar buku | Query: `penulis` (opsional), `terbit_setelah` (opsional, bilangan bulat), `batas` (bilangan bulat, default 10) |
| `GET /buku/terbaru` | Buku dengan tahun terbit terbesar | Tidak ada |
| `GET /buku/{buku_id}` | Detail satu buku | Path: `buku_id` (bilangan bulat) |

Aturan tambahan:

- Pencarian `penulis` tidak membedakan huruf besar dan kecil.
- Jika `penulis` dan `terbit_setelah` diberikan bersamaan, keduanya berlaku (hasil harus memenuhi keduanya).
- `terbit_setelah=2020` berarti tahun **lebih besar** dari 2020.

## Langkah pengerjaan

Kerjakan sendiri dulu secara bertahap. Setiap langkah bisa diuji sebelum lanjut.

1. **Kerangka.** Buat objek `FastAPI` dengan `title` dan `version`, lalu list `DAFTAR_BUKU`. Tulis `GET /status`. Pilih `def` atau `async def`: endpoint ini tidak menunggu apa pun, jadi aturan di [Dasar Async/Await](async-await.md) menyarankan `async def`.
2. **Detail buku.** Tulis `GET /buku/{buku_id}` dengan `buku_id: int`. Telusuri list untuk mencari id yang cocok.
3. **Daftar buku dengan filter.** Tulis `GET /buku` dengan tiga query parameter. Saring list berdasarkan parameter yang dikirim, lalu batasi jumlahnya.
4. **Buku terbaru.** Tulis `GET /buku/terbaru`. **Pikirkan dulu letaknya** relatif terhadap `GET /buku/{buku_id}`.

## Kode referensi

Jangan buka sebelum mencoba sendiri.

??? success "Tampilkan kode referensi"
    ```python title="main.py"
    --8<-- "fastapi/02-dasar-routing/latihan-gabungan/main.py"
    ```

### Penjelasan

| Bagian | Penjelasan |
|---|---|
| `async def status()` | Tidak menunggu apa pun, jadi memakai `async def` |
| `def daftar_buku(...)` | Memakai `def` biasa. Tidak ada `await`, dan kode seperti ini aman dijalankan sebagai `def` |
| `penulis: str \| None = None` | Query parameter opsional. Filter dipakai hanya jika nilainya bukan `None` |
| `terbit_setelah: int \| None = None` | Query parameter opsional bertipe bilangan bulat |
| `batas: int = 10` | Query parameter ber-default |
| `.lower()` pada kedua sisi | Membuat pencarian penulis tidak peka huruf besar-kecil |
| `/buku/terbaru` ditulis **sebelum** `/buku/{buku_id}` | Path tetap harus lebih dulu, agar `terbaru` tidak dibaca sebagai `buku_id` |
| `max(DAFTAR_BUKU, key=lambda b: b["tahun"])` | Mengambil buku dengan tahun terbesar |

## Menjalankan dan menguji

```bash
fastapi dev main.py
```

Uji dengan `curl` (pengguna PowerShell: `curl.exe`; apit URL dengan tanda kutip bila memuat `&`):

```bash
curl -i "http://127.0.0.1:8000/status"
curl -i "http://127.0.0.1:8000/buku?penulis=Sari%20Dewi&terbit_setelah=2020"
```

Hasil dari eksekusi nyata, dengan isi `data` diringkas jadi nomor buku:

| Request | Status | Hasil |
|---|---|---|
| `GET /status` | `200 OK` | `{"status":"ok","jumlah_buku":4}` |
| `GET /buku` | `200 OK` | `jumlah` 4, buku 1 sampai 4 |
| `GET /buku?batas=2` | `200 OK` | `jumlah` 2, buku 1 dan 2 |
| `GET /buku?penulis=Sari%20Dewi` | `200 OK` | `jumlah` 2, buku 1 dan 3 |
| `GET /buku?penulis=sari%20dewi` | `200 OK` | `jumlah` 2, buku 1 dan 3 (tidak peka huruf besar-kecil) |
| `GET /buku?terbit_setelah=2020` | `200 OK` | `jumlah` 2, buku 2 dan 3 |
| `GET /buku?penulis=Sari%20Dewi&terbit_setelah=2020` | `200 OK` | `jumlah` 1, buku 3 |
| `GET /buku?penulis=tidak%20ada` | `200 OK` | `{"jumlah":0,"data":[]}` |
| `GET /buku/terbaru` | `200 OK` | buku 3, `FastAPI untuk Pemula`, 2023 |
| `GET /buku/2` | `200 OK` | buku 2, `Memahami HTTP` |
| `GET /buku/abc` | `422` | `int_parsing`, `loc` `["path","buku_id"]` |
| `GET /buku?batas=abc` | `422` | `int_parsing`, `loc` `["query","batas"]` |
| `GET /buku?terbit_setelah=dua` | `422` | `int_parsing`, `loc` `["query","terbit_setelah"]` |

Contoh body lengkap untuk `GET /buku/terbaru`:

```json
{"id":3,"judul":"FastAPI untuk Pemula","penulis":"Sari Dewi","tahun":2023}
```

Pada `/openapi.json`, aplikasi tercatat dengan judul `Katalog Buku` versi `0.1.0`. Endpoint-nya terdaftar berurutan: `/status`, `/buku`, `/buku/terbaru`, `/buku/{buku_id}`. Parameter `penulis`, `terbit_setelah`, dan `batas` pada `/buku` semuanya `query` dan tidak wajib.

## Keterbatasan yang perlu kamu ketahui

`GET /buku/99` (buku tidak ada) menghasilkan **`200 OK`** dengan body `{"pesan":"Buku tidak ditemukan"}`. Itu kurang tepat: dari sudut pandang HTTP, buku yang tidak ada seharusnya berstatus `404`, supaya klien bisa membedakannya tanpa membaca isi pesan. Cara mengembalikan status error yang benar dibahas di [HTTPException](../04-penanganan-error/http-exception.md) (Modul 04: [Penanganan Error](../04-penanganan-error/index.md)). Untuk saat ini, anggap ini keterbatasan yang disengaja.

Keterbatasan lain: data hanya ada di memori, jadi tidak bertahan setelah server dihentikan, dan nilai seperti `batas=-1` tidak dibatasi (lihat [Query Parameter](query-parameter.md#4-nilai-yang-masuk-akal-secara-tipe-tetapi-tidak-masuk-akal-secara-makna)).

## Kesalahan umum

### 1. `/buku/terbaru` ditulis setelah `/buku/{buku_id}`

Pada pengujian dengan urutan terbalik, `GET /buku/terbaru` menghasilkan `422` dengan `loc` `["path","buku_id"]`, karena kata `terbaru` dicocokkan lebih dulu dengan `{buku_id}`. **Solusi:** pindahkan path tetap ke atas. Penjelasan lengkap ada di [Urutan Route](urutan-route.md).

### 2. Nama parameter tidak sama di path dan fungsi

Jika path-nya `/buku/{id_buku}` tetapi fungsinya menerima `buku_id`, nilainya dibaca sebagai query parameter wajib dan request gagal. Lihat [Path Parameter](path-parameter.md#2-nama-di-path-berbeda-dengan-nama-argumen).

### 3. Mengirim nilai bukan angka

`terbit_setelah=dua` ditolak `422`. Perhatikan bahwa `loc` selalu menunjukkan bagian URL (`path` atau `query`) dan nama parameternya.

## Pemeriksaan mandiri

Aplikasimu sudah benar jika:

- [ ] Kelima baris pertama pada tabel hasil di atas sama persis dengan keluaranmu.
- [ ] `GET /buku/terbaru` mengembalikan buku 3, bukan error.
- [ ] Filter `penulis` dan `terbit_setelah` bisa dipakai sendiri-sendiri maupun bersamaan.
- [ ] Nilai bukan angka pada `batas` dan `buku_id` menghasilkan `422`.
- [ ] Kamu bisa menjelaskan mengapa `/status` memakai `async def` dan `/buku` memakai `def`.

## Tantangan tambahan

Kerjakan setelah versi dasar berjalan:

1. Tambahkan query parameter `urut` pada `/buku` yang berisi `tahun` atau `judul`, lalu urutkan hasilnya. Apa yang terjadi jika nilainya yang lain?
2. Tambahkan endpoint `GET /penulis/{nama}/buku` yang mengembalikan buku milik satu penulis. Perhatikan nama yang mengandung spasi.

Kedua tantangan ini tidak punya kunci jawaban di sini. Dokumentasi resmi FastAPI dan materi di Modul 03 akan membantu untuk pembatasan nilai.

## Ringkasan

- Aplikasi nyata memakai gabungan path parameter, query parameter, dan urutan route.
- Path parameter menunjuk satu sumber daya, query parameter menyaring dan membatasi.
- Path tetap (`/buku/terbaru`) harus ditulis sebelum path berparameter (`/buku/{buku_id}`).
- `async def` untuk endpoint yang tidak memanggil kode yang memblokir dan tidak butuh menunggu, `def` biasa untuk selainnya atau bila ragu.
- Error `422` menunjukkan di bagian mana (`path` atau `query`) dan parameter mana yang salah.
- Aplikasi ini masih punya keterbatasan: status `200` untuk buku yang tidak ada, data hanya di memori, dan nilai belum dibatasi. Semuanya dibahas di modul berikutnya.

## Langkah berikutnya

Kembali ke daftar materi di [Modul 02: Dasar Routing](index.md), atau lanjut ke [Modul 03: Data dan Validasi](../03-data-validasi/index.md).
