# Proyek Praktik Tahap 4

## Tujuan pembelajaran

Setelah mengerjakan halaman ini, kamu mampu:

- [ ] Menambahkan pengguna, pendaftaran, dan login berbasis token ke proyek yang sudah berjalan.
- [ ] Menyimpan kata sandi sebagai hash dan tidak pernah mengembalikannya.
- [ ] Melindungi semua endpoint tugas, dan membatasi data per pemilik.
- [ ] Menerapkan otorisasi peran (`anggota` dan `pengelola`) dan kepemilikan.
- [ ] Menulis migrasi yang menambah tabel dan kolom berelasi pada SQLite dengan `batch_alter_table`.
- [ ] Memasang CORS untuk frontend yang sah.

## Prasyarat

- Sudah mengerjakan [Proyek Praktik Tahap 3](../06-basis-data/proyek-tahap-3.md).
- Sudah membaca seluruh materi Modul 07: [Hashing Password](hashing-password.md), [Token](token.md), [Proteksi Endpoint](proteksi-endpoint.md), [Otorisasi](otorisasi.md), dan [CORS](cors.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **SQLModel 0.0.48**, **Alembic 1.20.1**, **PyJWT 2.15.1**, dan **pwdlib 0.3.1** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Tentang tahap ini

Tahap 4 melanjutkan **TugasKu API**. Sampai tahap 3, siapa pun bisa membaca dan mengubah semua tugas. Kini setiap tugas punya pemilik, dan hanya pemilik (atau pengelola) yang bisa mengaksesnya.

| Aspek | Tahap 3 | Tahap 4 |
|---|---|---|
| Pengguna | tidak ada | tabel `pengguna` dengan hash kata sandi dan peran |
| Akses | terbuka untuk semua | wajib login (token Bearer) |
| Tugas | milik bersama | punya `pemilik_id` |
| Peran | tidak ada | `anggota` dan `pengelola` |
| Kategori | siapa saja bisa membuat | hanya `pengelola` yang membuat |
| Judul unik | di seluruh tabel | per pemilik |
| CORS | tidak ada | hanya origin frontend yang diizinkan |
| Kunci rahasia | tidak ada | `SECRET_KEY` dari variabel environment |

### Kebutuhan

| Operasi | Method dan path | Siapa yang boleh |
|---|---|---|
| Daftar | `POST /daftar` | siapa saja |
| Login | `POST /token` | siapa saja |
| Profil | `GET /saya` | pengguna login |
| Buat kategori | `POST /kategori` | `pengelola` |
| Daftar kategori | `GET /kategori` | pengguna login |
| Buat tugas | `POST /tugas` | pengguna login (pemilik = pembuat) |
| Daftar tugas | `GET /tugas` | pengguna login; anggota melihat miliknya, pengelola melihat semua |
| Baca, ganti, ubah, hapus tugas | `/tugas/{id}` | pemilik atau `pengelola` |

## Struktur proyek

Kode lengkap ada di `examples/fastapi/proyek/tahap-4/`:

| Berkas | Fungsi |
|---|---|
| `models.py` | Model tabel dan skema (menambah `Pengguna` dan `pemilik_id`) |
| `main.py` | Aplikasi: konfigurasi, error, autentikasi, dan endpoint |
| `buat_pengelola.py` | Skrip untuk membuat akun pengelola pertama |
| `alembic.ini`, `alembic/` | Migrasi, termasuk revisi baru untuk tahap ini |

## Langkah menjalankan

```powershell
pip install "fastapi[standard]" sqlmodel alembic pyjwt "pwdlib[argon2]"
$env:SECRET_KEY = "isi-dengan-kunci-acak-hasil-perintah-di-halaman-token"
alembic upgrade head
python buat_pengelola.py rina "sandi-rina-789"
fastapi dev main.py
```

Urutannya penting:

1. `SECRET_KEY` harus diisi sebelum server dijalankan (`buat_pengelola.py` tidak membutuhkannya). Cara membuat kunci ada di [Token](token.md).
2. `alembic upgrade head` membuat atau memperbarui tabel.
3. `buat_pengelola.py` membuat akun pengelola pertama. Pendaftaran lewat API selalu menghasilkan `anggota`, jadi pengelola tidak bisa dibuat dari luar.

Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah. Kata sandi `sandi-rina-789` hanya contoh.

## Kode lengkap

### `models.py`

```python title="models.py"
--8<-- "fastapi/proyek/tahap-4/models.py"
```

### `main.py`

```python title="main.py"
--8<-- "fastapi/proyek/tahap-4/main.py"
```

### `buat_pengelola.py`

```python title="buat_pengelola.py"
--8<-- "fastapi/proyek/tahap-4/buat_pengelola.py"
```

### Revisi migrasi tahap 4

```python title="alembic/versions/2c172ef5d2ca_tambah_pengguna_dan_pemilik_tugas.py"
--8<-- "fastapi/proyek/tahap-4/alembic/versions/2c172ef5d2ca_tambah_pengguna_dan_pemilik_tugas.py"
```

## Penjelasan kode

### Model

- `Pengguna` adalah tabel baru: `nama_pengguna` (unik dan berindeks), `hash_kata_sandi`, dan `peran`. Kata sandi tidak pernah disimpan apa adanya.
- `PenggunaBuat` adalah skema masuk (kata sandi), `PenggunaPublik` adalah skema keluar (tanpa hash), dan `Token` adalah respons login. Pola ini sama dengan [Model dan Skema](../06-basis-data/model-dan-skema.md).
- `Tugas` mendapat `pemilik_id` (foreign key ke `pengguna.id`) dan relasi `pemilik`. `pemilik_id` bersifat opsional agar tugas dari tahap 3 tetap valid.
- `TugasBuat` tidak memuat `pemilik_id`, sehingga klien tidak bisa menentukannya. Hanya `TugasPublik` yang menampilkannya.

### Konfigurasi dan CORS

`SECRET_KEY` dibaca dari environment; aplikasi menolak mulai bila kosong. `CORSMiddleware` hanya mengizinkan origin di `ORIGIN_DIIZINKAN` (di contoh, `http://localhost:3000`) dan method serta header yang dibutuhkan. Ingat dari [CORS](cors.md): ini mengatur apa yang boleh dibaca browser, bukan melindungi API; perlindungan datang dari autentikasi.

### Autentikasi

- `buat_token` membuat JWT dengan `sub` berisi nama pengguna dan masa berlaku 30 menit.
- `pengguna_saat_ini` memverifikasi token, lalu mencari pengguna di basis data lewat `sub`. Bedanya dengan halaman Proteksi Endpoint: penggunanya kini diambil dari tabel `pengguna`, dan dependency ini juga bergantung pada `SessionDep`. Semua kegagalan token dijawab satu `401`.
- `/daftar` menolak nama yang sudah ada (`409`), meng-hash kata sandi, dan selalu membuat peran `anggota`.
- `/token` memverifikasi kata sandi dengan hash tiruan agar waktu respons seragam, seperti di [Hashing Password](hashing-password.md).

### Otorisasi

- `wajib_pengelola` menolak pengguna yang bukan `pengelola` dengan `403`. Dipakai untuk membuat kategori.
- `tugas_yang_boleh_diakses` mengambil tugas, menjawab `404` bila tidak ada, dan `403` bila pemanggil bukan pemilik dan bukan pengelola. Dipakai bersama oleh `GET`, `PUT`, `PATCH`, dan `DELETE` pada `/tugas/{id}`, sehingga aturan kepemilikan ditulis sekali.
- `daftar_tugas` menyaring: anggota hanya melihat tugas dengan `pemilik_id` miliknya.
- `buat_tugas` mengisi `pemilik_id` dari pengguna yang login (`update={"pemilik_id": pengguna.id}`), bukan dari body.
- `pastikan_judul_unik` kini menerima `pemilik_id`, sehingga dua pengguna boleh punya tugas berjudul sama.

### Penanganan error

Format `{"galat": ...}` dari tahap 2 dan 3 dipertahankan, dengan dua perubahan. Handler `StarletteHTTPException` kini meneruskan `headers` (agar `WWW-Authenticate: Bearer` ikut pada `401`), dan ada exception baru `NamaPenggunaSudahAda` (`409`).

### Migrasi

Revisi tahap 4 menambah tabel `pengguna` dan kolom `pemilik_id` beserta foreign key pada `tugas`. Hasil autogenerate perlu diperbaiki, dijelaskan di bagian berikutnya.

## Jebakan migrasi: foreign key di SQLite

Revisi yang dihasilkan otomatis memakai `op.add_column(...)` lalu `op.create_foreign_key(None, ...)`. Menjalankannya (`alembic upgrade head`) pada SQLite gagal:

```text
NotImplementedError: No support for ALTER of constraints in SQLite dialect. Please refer to the batch mode feature which allows for SQLite migrations using a copy-and-move strategy.
```

Seperti jebakan di [Migrasi](../06-basis-data/migrasi.md), perubahan sebelum kegagalan sudah sempat diterapkan: tabel `pengguna` dan kolom `pemilik_id` tercipta, tetapi nomor revisi tidak berubah. Dalam percobaan, pemulihan dilakukan dengan membuat ulang basis data uji.

Perbaikannya ada di berkas revisi final di atas:

```python
with op.batch_alter_table('tugas', schema=None) as batch_op:
    batch_op.add_column(sa.Column('pemilik_id', sa.Integer(), nullable=True))
    batch_op.create_foreign_key('fk_tugas_pemilik_id_pengguna', 'pengguna', ['pemilik_id'], ['id'])
```

- `batch_alter_table` membuat salinan tabel dengan struktur baru, memindahkan datanya, lalu mengganti tabel lama (strategi *copy-and-move* yang disebut pada pesan galat).
- Constraint diberi nama (`fk_tugas_pemilik_id_pengguna`). Hasil autogenerate memakai `None`, dan Alembic memperingatkan di `downgrade` bahwa nama `None` akan gagal.

Hasil setelah perbaikan (basis data uji berisi satu tugas dari tahap 3):

```text
Running upgrade 8a4eeca129c7 -> 2c172ef5d2ca, tambah pengguna dan pemilik tugas
('Tugas dari tahap 3', None, 2, 0, None, 1, None)
No new upgrade operations detected.
```

Data tahap 3 selamat, dengan `pemilik_id` kosong. `downgrade -1` lalu `upgrade head` juga berjalan. Tugas tanpa pemilik hanya bisa diakses `pengelola` (lihat di bawah).

## Mencoba request

Hasil di bawah dijalankan berurutan dengan `curl.exe` dari basis data tahap 3 yang sudah dimigrasi dan berisi satu tugas lama. Pengelola `rina` dibuat dengan `buat_pengelola.py`; `budi` dan `sari` mendaftar lewat API. Header yang dipakai: `Authorization: Bearer <token>`.

### Pendaftaran dan login

| Request | Status | Isi |
|---|---|---|
| `POST /daftar` `budi` | `201` | `{"id":2,"nama_pengguna":"budi","peran":"anggota"}` |
| `POST /daftar` `sari` | `201` | `{"id":3,"nama_pengguna":"sari","peran":"anggota"}` |
| `POST /daftar` `budi` (ulang) | `409` | `{"galat":{"kode":"NAMA_PENGGUNA_SUDAH_ADA",...}}` |
| `POST /daftar` nama dan kata sandi terlalu pendek | `422` | `VALIDASI_GAGAL` dengan dua rincian |
| `POST /token` kata sandi salah | `401` | `HTTP_401`, header `www-authenticate: Bearer` |
| `GET /saya` (token budi) | `200` | `{"id":2,"nama_pengguna":"budi","peran":"anggota"}` |
| `GET /tugas` tanpa token | `401` | `{"galat":{"kode":"HTTP_401","pesan":"Not authenticated",...}}` |

Respons pendaftaran tidak memuat kata sandi maupun hash.

### Kategori (hanya pengelola)

| Request | Status | Isi |
|---|---|---|
| `POST /kategori` oleh `budi` | `403` | `{"galat":{"kode":"HTTP_403","pesan":"Hanya untuk pengelola",...}}` |
| `POST /kategori` oleh `rina` | `201` | `{"nama":"Kuliah","id":1}` |
| `GET /kategori` oleh `budi` | `200` | `[{"nama":"Kuliah","id":1}]` |

### Tugas dan kepemilikan

| Request | Status | Isi |
|---|---|---|
| `budi` `POST /tugas` "Belajar FastAPI" | `201` | tugas `id` 2, `"pemilik_id":2` |
| `budi` `POST /tugas` "belajar fastapi" | `409` | `JUDUL_SUDAH_ADA` |
| `sari` `POST /tugas` "belajar fastapi" | `201` | tugas `id` 3, `"pemilik_id":3` |
| `budi` `POST /tugas` kategori 99 | `404` | `KATEGORI_TIDAK_ADA` |
| `GET /tugas` oleh `budi` | `200` | hanya tugas 2 dan 4 (miliknya) |
| `GET /tugas` oleh `sari` | `200` | hanya tugas 3 |
| `GET /tugas` oleh `rina` | `200` | semua, termasuk tugas dari tahap 3 (`"pemilik_id":null`) |
| `sari` `GET /tugas/2` (milik budi) | `403` | `Tugas ini bukan milikmu` |
| `sari` `GET /tugas/1` (dari tahap 3, tanpa pemilik) | `403` | pesan yang sama |
| `rina` `GET /tugas/1` | `200` | `"pemilik_id":null,"kategori":null` |
| `budi` `GET /tugas/2` | `200` | tugas dengan `"kategori":{"nama":"Kuliah","id":1}` |
| `budi` `PATCH /tugas/2` `{"selesai":true}` | `200` | `"selesai":true` |
| `budi` `PATCH /tugas/2` `{"judul":null}` | `400` | `Field 'judul' tidak boleh null` |
| `sari` `DELETE /tugas/2` | `403` | `Tugas ini bukan milikmu` |
| `budi` `DELETE /tugas/2` | `204` | tanpa isi |
| `budi` `GET /tugas/99` | `404` | `TUGAS_TIDAK_ADA` |

### CORS

Preflight `OPTIONS /tugas/2` dengan `Origin: http://localhost:3000`, `Access-Control-Request-Method: PATCH`, dan `Access-Control-Request-Headers: Authorization` dijawab `200` dengan `access-control-allow-origin: http://localhost:3000`. Perilaku di browser **tidak diuji**.

!!! warning "Keterbatasan tahap 4"
    - Tidak ada kedaluwarsa atau pencabutan token selain masa berlaku 30 menit (dan hapus pengguna). Token tidak bisa dicabut seketika.
    - Tidak ada pembatasan percobaan login (*rate limiting*), pemulihan kata sandi, atau verifikasi email.
    - Peran hanya bisa diatur lewat skrip atau basis data, bukan lewat API.
    - Tugas tahap 3 yang tidak punya pemilik hanya dapat diakses `pengelola`; tidak ada alat untuk menetapkan pemiliknya.
    - Aplikasi belum dijalankan lewat HTTPS; token Bearer sebaiknya hanya dikirim lewat HTTPS pada aplikasi nyata.
    - CORS dan tombol *Authorize* di `/docs` belum diverifikasi lewat browser.
    - `500` belum diuji untuk proyek ini.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Lupa mengisi `SECRET_KEY` | `main.py` menolak mulai dengan `RuntimeError` yang menjelaskan cara membuat kunci (diuji pada contoh di halaman Token). |
| Menjalankan server sebelum `alembic upgrade head` | Tabel `pengguna` belum ada. Tidak dijalankan di sini; urutannya dijelaskan di atas. |
| Memakai revisi autogenerate tanpa `batch_alter_table` untuk foreign key di SQLite | `NotImplementedError` dan migrasi setengah jalan (teruji). |
| Mengambil `pemilik_id` dari body | Klien bisa membuat tugas atas nama orang lain. Ambil dari pengguna yang login. |
| Mengembalikan semua tugas lalu menyaring di klien | Data orang lain bocor. Saring di server (teruji pada `GET /tugas`). |
| Membuat endpoint pembuat pengelola yang terbuka | Siapa saja bisa menjadi pengelola. Pakai skrip yang dijalankan pemilik server. |
| Menyimpan kunci di Git | Kunci bocor. Pakai variabel environment. |

## Latihan

1. **Dasar.** Mengapa pendaftaran lewat API selalu menghasilkan `anggota`?
2. **Prediksi.** Apa status `sari` membaca tugas 1 (tugas lama tanpa pemilik)? Mengapa?
3. **Migrasi.** Mengapa revisi tahap 4 memakai `batch_alter_table`, dan apa yang terjadi bila tidak?
4. **Analisis.** Mengapa keunikan judul sekarang per pemilik?

??? success "Kunci jawaban"
    Jawaban 2 sampai 4 mengacu pada hasil uji di atas. Jawaban 1 adalah penalaran dari kode.

    1. Agar pengguna tidak bisa menaikkan hak sendiri. Peran hanya ditetapkan oleh pemilik server lewat `buat_pengelola.py` atau langsung di basis data.
    2. `403` dengan `Tugas ini bukan milikmu`: `pemilik_id` tugas itu `null`, jadi bukan milik `sari`, dan `sari` bukan pengelola.
    3. SQLite tidak mendukung penambahan constraint lewat `ALTER`. Tanpa `batch_alter_table`, `alembic upgrade head` gagal dengan `NotImplementedError: No support for ALTER of constraints in SQLite dialect` dan meninggalkan basis data setengah jalan.
    4. Dua pengguna wajar punya tugas berjudul sama (teruji: `sari` berhasil membuat "belajar fastapi" padahal `budi` sudah punya). Keunikan global akan bocor informasi milik pengguna lain dan memaksa mereka mengubah judul.

## Ringkasan

- Tahap 4 menambah pengguna, login berbasis token, dan kepemilikan data pada TugasKu API.
- Kata sandi disimpan sebagai hash Argon2; respons tidak pernah memuat kata sandi maupun hash.
- Semua endpoint tugas wajib login; `pemilik_id` diisi dari pengguna login, dan akses dibatasi pada pemilik atau pengelola.
- Otorisasi peran (`pengelola`) dan kepemilikan memakai dependency yang ditulis sekali dan dipakai berulang.
- Migrasi foreign key di SQLite butuh `batch_alter_table` dan nama constraint.
- Kunci rahasia datang dari environment, dan CORS hanya mengizinkan origin frontend.

## Langkah berikutnya

Kembali ke [Modul 07: Autentikasi dan Keamanan](index.md). Modul berikutnya adalah [Modul 08: Struktur Proyek](../08-struktur-proyek/index.md).
