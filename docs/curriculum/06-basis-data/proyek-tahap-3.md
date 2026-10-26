# Proyek Praktik Tahap 3

## Tujuan pembelajaran

Setelah mengerjakan halaman ini, kamu mampu:

- [ ] Memindahkan penyimpanan proyek dari memori ke basis data tanpa mengubah perilaku API.
- [ ] Menyusun model tabel, skema input, dan skema output untuk `Tugas` dan `Kategori`.
- [ ] Mengelola tabel dengan migrasi Alembic sejak awal proyek.
- [ ] Mempertahankan format error terstruktur dari tahap 2.
- [ ] Memastikan data bertahan setelah server dimulai ulang.

## Prasyarat

- Sudah mengerjakan [Proyek Praktik Tahap 2](../04-penanganan-error/proyek-tahap-2.md).
- Sudah membaca seluruh materi Modul 06: [Koneksi](koneksi-basis-data.md), [Model dan Skema](model-dan-skema.md), [Operasi CRUD](operasi-crud.md), [Relasi](relasi.md), dan [Migrasi](migrasi.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **SQLModel 0.0.48**, **SQLAlchemy 2.1.6**, dan **Alembic 1.20.1** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Tentang tahap ini

Tahap 3 melanjutkan **TugasKu API**. Endpoint dan aturan dari tahap 2 dipertahankan; yang berubah adalah tempat data disimpan.

| Aspek | Tahap 2 | Tahap 3 |
|---|---|---|
| Penyimpanan | `dict` di memori (hilang saat restart) | SQLite lewat SQLModel |
| Model | satu set model Pydantic | model tabel + skema input/output |
| Struktur tabel | tidak ada | dikelola Alembic |
| Relasi | tidak ada | `Kategori` satu-ke-banyak `Tugas` |
| Format error | `{"galat": ...}` | sama, dengan tambahan `KATEGORI_TIDAK_ADA` |
| Judul unik | pemeriksaan di `dict` | pemeriksaan lewat kueri, tidak peka huruf besar-kecil |

### Kebutuhan

| Operasi | Method dan path | Sukses | Kemungkinan error |
|---|---|---|---|
| Buat kategori | `POST /kategori` | `201` | `422` |
| Daftar kategori | `GET /kategori` | `200` | |
| Buat tugas | `POST /tugas` | `201` | `422`, `404` kategori, `409` judul kembar |
| Daftar tugas | `GET /tugas` | `200` | `422` |
| Ambil satu (dengan kategori) | `GET /tugas/{id}` | `200` | `404`, `422` |
| Ganti | `PUT /tugas/{id}` | `200` | `404`, `409`, `422` |
| Ubah sebagian | `PATCH /tugas/{id}` | `200` | `400`, `404`, `409`, `422` |
| Hapus | `DELETE /tugas/{id}` | `204` | `404`, `422` |

## Struktur proyek

Kode lengkap ada di `examples/fastapi/proyek/tahap-3/`:

| Berkas | Fungsi |
|---|---|
| `models.py` | Model tabel dan skema |
| `main.py` | Aplikasi, penanganan error, dan endpoint |
| `alembic.ini`, `alembic/` | Konfigurasi dan revisi migrasi |

## Langkah menjalankan

```powershell
pip install "fastapi[standard]" sqlmodel alembic
alembic upgrade head
fastapi dev main.py
```

Urutannya penting: `alembic upgrade head` **sebelum** server, karena aplikasi ini tidak membuat tabel sendiri. Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah.

## Kode lengkap

### `models.py`

```python title="models.py"
--8<-- "fastapi/proyek/tahap-3/models.py"
```

### `main.py`

```python title="main.py"
--8<-- "fastapi/proyek/tahap-3/main.py"
```

### Revisi migrasi pertama

```python title="alembic/versions/8a4eeca129c7_buat_tabel_kategori_dan_tugas.py"
--8<-- "fastapi/proyek/tahap-3/alembic/versions/8a4eeca129c7_buat_tabel_kategori_dan_tugas.py"
```

Berkas ini dihasilkan otomatis dengan `alembic revision --autogenerate -m "buat tabel kategori dan tugas"`. Setelah dibaca, tidak ada yang perlu diperbaiki karena semua kolom wajib berada di tabel yang baru dibuat, bukan ditambahkan ke tabel berisi data (bandingkan dengan jebakan di [Migrasi](migrasi.md)). Konfigurasi `alembic.ini` dan `alembic/env.py` sama dengan contoh di halaman Migrasi: alamat `sqlite:///database.db` dan `target_metadata = SQLModel.metadata`.

## Penjelasan kode

### Model dan skema

Pola pewarisan dari [Model dan Skema](model-dan-skema.md) diterapkan pada dua entitas:

- `TugasDasar` memuat field bersama beserta aturan validasi, dan `kategori_id` dengan `foreign_key="kategori.id"`.
- `Tugas` (`table=True`) menambah `id` dan atribut `kategori` (relasi).
- `TugasBuat`, `TugasUbah` (semua field opsional), `TugasPublik` (menambah `id`), dan `TugasDenganKategori` (menyertakan objek kategori) adalah skema untuk input dan output.
- `Kategori` mengikuti pola yang sama, dengan `tugas: list["Tugas"]` sebagai sisi lain relasi.

### Penanganan error

Bagian `exception` dan `handler` dipindahkan dari tahap 2 dengan satu tambahan, `KategoriTidakDitemukan` (`404`), karena `kategori_id` kini harus merujuk kategori yang ada. Alasan pemeriksaan manual itu ada di [Relasi](relasi.md): SQLite pada pengaturan ini tidak menolak `kategori_id` yang tidak ada.

### Session dan fungsi pembantu

```python
def get_session():
    with Session(engine) as session:
        yield session
```

Dependency `yield` dari [Dependency dengan yield](../05-dependency-injection/dependency-yield.md): satu session per request, ditutup otomatis. Tiga fungsi pembantu mengelompokkan pemeriksaan yang dipakai berulang:

- `cari_tugas` mengambil tugas atau melempar `TugasTidakDitemukan`.
- `pastikan_kategori_ada` memeriksa `kategori_id` bila diisi.
- `pastikan_judul_unik` mencari tugas dengan judul yang sama tanpa memperhatikan huruf besar-kecil (`ilike`). Parameter `abaikan_id` mencegah tugas dianggap bentrok dengan dirinya sendiri saat diubah.

### Endpoint

- **Buat**: periksa kategori, periksa judul, baru simpan (`add`, `commit`, `refresh`). Pemeriksaan di depan agar tidak ada data berubah bila ada error.
- **Daftar**: kueri `select(Tugas)` dirangkai dengan `where` untuk filter `selesai`, `kategori_id`, dan `cari`, lalu `offset` dan `limit` untuk paginasi.
- **Ambil satu**: memakai `TugasDenganKategori`, sehingga respons menyertakan objek kategori.
- **Ganti** (`PUT`): mengganti seluruh field dari `TugasBuat`.
- **Ubah sebagian** (`PATCH`): `model_dump(exclude_unset=True)`, menolak `null` untuk `judul`, `prioritas`, dan `selesai` dengan `400` (pelajaran dari temuan `500` di [Operasi CRUD](operasi-crud.md)), lalu `sqlmodel_update`.
- **Hapus**: `session.delete` lalu `commit`, dengan jawaban `204`.

## Mencoba request

Hasil di bawah dijalankan berurutan dengan `curl.exe` dari keadaan setelah `alembic upgrade head` (basis data kosong). Body dikirim dari berkas JSON dengan header `Content-Type: application/json`.

### Kategori

| Request | Status | Isi |
|---|---|---|
| `POST /kategori` `{"nama":"Kuliah"}` | `201` | `{"nama":"Kuliah","id":1}` |
| `POST /kategori` `{"nama":"Rumah"}` | `201` | `{"nama":"Rumah","id":2}` |
| `GET /kategori` | `200` | `[{"nama":"Kuliah","id":1},{"nama":"Rumah","id":2}]` |

### Membuat tugas

| Body | Status | Isi |
|---|---|---|
| `{"judul":"Belajar FastAPI","catatan":"Modul 06","prioritas":1,"kategori_id":1}` | `201` | `{"judul":"Belajar FastAPI","catatan":"Modul 06","prioritas":1,"selesai":false,"kategori_id":1,"id":1}` |
| `{"judul":"belajar fastapi"}` | `409` | `{"galat":{"kode":"JUDUL_SUDAH_ADA","pesan":"Judul 'belajar fastapi' sudah dipakai","rincian":[]}}` |
| `{"judul":"Cuci motor","kategori_id":2}` | `201` | tugas `id` 2 |
| `{"judul":"Tugas hantu","kategori_id":99}` | `404` | `{"galat":{"kode":"KATEGORI_TIDAK_ADA","pesan":"Kategori dengan id 99 tidak ditemukan","rincian":[]}}` |
| `{"judul":"ab","prioritas":9}` | `422` | `VALIDASI_GAGAL` dengan dua rincian: `body.judul` (`string_too_short`) dan `body.prioritas` (`less_than_equal`) |

### Membaca

| Request | Status | Isi |
|---|---|---|
| `GET /tugas` | `200` | tugas 1 dan 2 |
| `GET /tugas?kategori_id=2` | `200` | hanya "Cuci motor" |
| `GET /tugas?cari=motor` | `200` | hanya "Cuci motor" |
| `GET /tugas/1` | `200` | tugas 1 dengan `"kategori":{"nama":"Kuliah","id":1}` |
| `GET /tugas/99` | `404` | `TUGAS_TIDAK_ADA` |
| `GET /tugas/0` | `422` | `VALIDASI_GAGAL`, `"field":"path.tugas_id"` |

### Mengubah dan menghapus

| Request | Status | Isi |
|---|---|---|
| `PATCH /tugas/1` `{"selesai":true,"catatan":null}` | `200` | `{"judul":"Belajar FastAPI","catatan":null,"prioritas":1,"selesai":true,"kategori_id":1,"id":1}` |
| `GET /tugas?selesai=true` | `200` | hanya tugas 1 |
| `PATCH /tugas/1` `{"judul":null}` | `400` | `{"galat":{"kode":"HTTP_400","pesan":"Field 'judul' tidak boleh null","rincian":[]}}` |
| `PATCH /tugas/1` `{"judul":"Cuci motor"}` | `409` | `JUDUL_SUDAH_ADA` |
| `PATCH /tugas/1` `{"kategori_id":99}` | `404` | `KATEGORI_TIDAK_ADA` |
| `PUT /tugas/1` `{"judul":"Belajar FastAPI lanjut","prioritas":1}` | `200` | `catatan` dan `selesai` kembali ke nilai bawaan, `kategori_id` menjadi `null` |
| `DELETE /tugas/2` | `204` | tanpa isi |
| `DELETE /tugas/2` (ulang) | `404` | `TUGAS_TIDAK_ADA` |

Perhatikan baris `PUT`: seperti di tahap 1, `PUT` mengganti seluruh data, jadi field yang tidak dikirim (`catatan`, `kategori_id`, `selesai`) kembali ke nilai bawaan. Di sinilah `PATCH` lebih aman untuk ubah sebagian.

### Data bertahan

Setelah server dihentikan dan dijalankan lagi, data tetap ada. Diuji dengan menjalankan aplikasi baru pada basis data yang sama: `GET /tugas` mengembalikan tugas "Belajar FastAPI lanjut" dari sesi sebelumnya. Inilah perbedaan terpenting dengan tahap 1 dan 2.

!!! warning "Keterbatasan tahap 3"
    - Tidak ada pengguna atau login; siapa pun bisa mengubah dan menghapus (Modul 07).
    - Keunikan judul diperiksa oleh kode, bukan oleh basis data. Dua request bersamaan berpotensi sama-sama lolos pemeriksaan; ini penalaran, tidak diuji.
    - `Kategori` belum bisa diubah atau dihapus lewat API.
    - `500` belum diuji untuk proyek ini (handler `Exception` identik dengan [Handler Error Kustom](../04-penanganan-error/handler-kustom.md)).
    - Tampilan Swagger UI belum diverifikasi lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Menjalankan server sebelum `alembic upgrade head` | Tabel belum ada, sehingga permintaan ke basis data gagal. Tidak dijalankan di sini; urutan ini dijelaskan di atas. |
| Menjalankan server dari folder yang berbeda | `database.db` baru dibuat di folder itu, sehingga data lama tampak hilang. |
| Mengubah model tanpa membuat revisi | `alembic check` melaporkan `New upgrade operations detected` (teruji di [Migrasi](migrasi.md)). |
| Memakai model tabel sebagai body | Tidak ada `422` yang andal; pakai `TugasBuat` dan `TugasUbah`. |
| Menyimpan data lalu memeriksa error | Periksa dulu, ubah belakangan. |
| Mengirim `database.db` ke Git | Berisi data; `*.db` diabaikan di `.gitignore` repositori ini. |

## Latihan

1. **Dasar.** Hentikan server, jalankan lagi, lalu `GET /tugas`. Apa yang kamu lihat dan mengapa?
2. **Endpoint baru.** Tambahkan `GET /kategori/{kategori_id}` yang menyertakan daftar tugasnya, dan jawab `404` bila kategori tidak ada.
3. **Migrasi.** Tambahkan kolom `tenggat: str | None = None` ke `TugasDasar`. Langkah apa saja yang perlu dilakukan agar tabel berubah tanpa menghapus data?
4. **Analisis.** Mengapa `pastikan_judul_unik` dipanggil sebelum `session.add`?

??? success "Kunci jawaban"
    Jawaban 1 dan 2 dijalankan. Jawaban 3 mengacu pada alur yang teruji di [Migrasi](migrasi.md). Jawaban 4 adalah penalaran.

    1. Daftar tugas yang sama masih ada, karena data disimpan di berkas `database.db`, bukan di variabel.
    2. Teruji dengan `TestClient`:

        ```python
        class KategoriDenganTugas(KategoriPublik):
            tugas: list[TugasPublik] = []


        @app.get("/kategori/{kategori_id}", response_model=KategoriDenganTugas)
        def ambil_kategori(kategori_id: int, session: SessionDep):
            kategori = session.get(Kategori, kategori_id)
            if kategori is None:
                raise KategoriTidakDitemukan(kategori_id)
            return kategori
        ```

        Hasil: `GET /kategori/3` menghasilkan `200` dengan daftar tugas milik kategori itu, dan `GET /kategori/99` menghasilkan `404` dengan `KATEGORI_TIDAK_ADA`.
    3. Tambahkan field di `TugasDasar`, jalankan `alembic revision --autogenerate -m "tambah tenggat"`, baca berkas revisi (kolom nullable tidak perlu `server_default`), lalu `alembic upgrade head`. Cadangkan `database.db` sebelumnya.
    4. Agar tidak ada data yang tersimpan bila judul ternyata kembar. Memeriksa dulu menjaga basis data tetap konsisten saat terjadi error.

## Ringkasan

- Tahap 3 memindahkan penyimpanan TugasKu API dari memori ke SQLite, tanpa mengubah kontrak API.
- Model tabel, skema input, dan skema output dipisah; relasi `Kategori` ke `Tugas` ditambahkan.
- Tabel dikelola oleh Alembic: `alembic upgrade head` dijalankan sebelum server.
- Pemeriksaan keberadaan kategori dan keunikan judul dilakukan oleh kode, sebelum menyimpan.
- Format error terstruktur dari tahap 2 tetap berlaku.
- Data bertahan setelah server dimulai ulang.

## Langkah berikutnya

Kembali ke [Modul 06: Basis Data](index.md). Modul berikutnya adalah [Modul 07: Autentikasi dan Keamanan](../07-autentikasi-keamanan/index.md).
