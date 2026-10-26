# Koneksi ke Basis Data

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan mengapa data perlu disimpan di basis data, bukan di variabel Python.
- [ ] Menjelaskan peran SQLite, SQLModel, *engine*, dan *session*.
- [ ] Membuat engine dan tabel saat aplikasi mulai dengan `lifespan`.
- [ ] Membuat dependency `yield` yang memberi satu session per request.
- [ ] Membuktikan data bertahan setelah server dimulai ulang.

## Prasyarat

- Selesai [Modul 05: Dependency Injection](../05-dependency-injection/index.md), terutama [Dependency dengan yield](../05-dependency-injection/dependency-yield.md).
- SQL dasar: `SELECT`, `INSERT`, `UPDATE`, `DELETE`.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **SQLModel 0.0.48**, dan **SQLAlchemy 2.1.6** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

!!! note "Pilihan teknologi untuk Modul 06"
    Modul ini memakai **SQLModel** dengan **SQLite**, sesuai tutorial basis data di dokumentasi resmi FastAPI. SQLModel dibangun di atas SQLAlchemy dan Pydantic. Pilihan ini menjaga fokus pada FastAPI; alternatif seperti SQLAlchemy langsung tidak dibahas. Dokumentasi FastAPI menyebut SQLite dipakai karena berupa satu berkas tanpa server, dan untuk produksi disarankan basis data server seperti PostgreSQL.

## Konsep

### Mengapa basis data

Di Modul 03 dan 04, tugas disimpan dalam variabel Python. Datanya **hilang** saat server dimulai ulang. **Basis data** menyimpan data di luar program sehingga bertahan, bisa dicari dengan cepat, dan bisa dipakai bersama.

### Bagian-bagiannya

| Istilah | Arti |
|---|---|
| **SQLite** | Basis data yang berupa satu berkas (di sini `database.db`), tanpa server terpisah. Mudah untuk belajar. |
| **SQLModel** | Library yang menghubungkan Python dengan basis data SQL. Satu kelas bisa sekaligus menjadi model Pydantic dan tabel. |
| **Engine** | Objek yang memegang koneksi ke basis data. Cukup satu untuk seluruh aplikasi. |
| **Session** | "Percakapan" dengan basis data: mencatat objek dan perubahannya, lalu `commit` untuk menyimpan. Satu per request. |
| **Model tabel** | Kelas dengan `table=True`; setiap objeknya adalah satu baris. |

### Pemasangan

SQLModel belum terpasang bersama FastAPI. Dengan venv aktif:

```powershell
pip install sqlmodel
```

Versi yang diuji tercatat di kotak versi di atas dan di `examples/fastapi/requirements.txt`.

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/06-basis-data/koneksi/main.py"
```

## Penjelasan kode

### Alamat dan engine

```python
sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
```

- `sqlite:///database.db` berarti SQLite dengan berkas `database.db` di **folder tempat server dijalankan**.
- `check_same_thread=False` mengizinkan FastAPI memakai koneksi SQLite dari beberapa *thread*. Dokumentasi FastAPI menjelaskan bahwa satu request bisa melewati beberapa thread, sehingga pengaturan ini diperlukan untuk SQLite.
- Engine dibuat **sekali**, di luar fungsi, dan dipakai ulang.

### Model tabel

```python
class Catatan(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    isi: str
```

- `table=True` menjadikan kelas ini tabel bernama `catatan`.
- `id` adalah kunci utama (*primary key*). Tipe `int | None` dengan default `None` membuat basis data yang mengisi nomornya, bukan klien.
- Model tabel dibahas mendalam di [Model dan Skema](model-dan-skema.md).

### Membuat tabel saat aplikasi mulai

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield
```

- `lifespan` menjalankan kode sebelum `yield` **sekali saat aplikasi mulai**, dan kode sesudahnya saat aplikasi berhenti. Pola ini mirip dependency `yield`.
- `create_all` membuat tabel untuk semua model tabel bila belum ada. Bila sudah ada, tidak diubah.
- Dokumentasi FastAPI menyebut `lifespan` sebagai cara yang dianjurkan, sedangkan `@app.on_event("startup")` dinyatakan usang (*deprecated*).
- `create_all` hanya membuat tabel baru; ia tidak mengubah tabel yang sudah ada. Untuk itu ada migrasi, dibahas di [Migrasi](migrasi.md).

### Session per request

```python
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
```

Ini dependency `yield` seperti di Modul 05: session dibuka sebelum `yield` dan ditutup otomatis oleh `with` sesudah request selesai. `SessionDep` adalah alias `Annotated` agar endpoint cukup menulis `session: SessionDep`.

### Endpoint

- `GET /db/ping` menjalankan `SELECT 1` untuk membuktikan koneksi hidup.
- `GET /db/tabel` menampilkan nama tabel yang ada.
- `POST /catatan` menambah baris: `session.add(...)` mendaftarkan objek, `session.commit()` menyimpannya, `session.refresh(...)` memuat ulang objek agar `id` yang dibuat basis data terisi.
- `GET /catatan` mengambil semua baris dengan `select(Catatan)`.

## Menjalankan

```powershell
pip install sqlmodel
fastapi dev main.py
```

Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah. Setelah server mulai, berkas `database.db` muncul di folder tempat perintah dijalankan.

## Mencoba request

Hasil di bawah dijalankan dengan `curl.exe`, dari keadaan tanpa berkas `database.db`.

```powershell
curl.exe http://127.0.0.1:8000/db/ping
curl.exe http://127.0.0.1:8000/db/tabel
```

```json
{"hasil":1}
{"tabel":["catatan"]}
```

Simpan `{"isi":"Belajar SQLModel"}` sebagai `c1.json`:

```powershell
curl.exe -i -X POST http://127.0.0.1:8000/catatan -H "Content-Type: application/json" -d "@c1.json"
```

```text
HTTP/1.1 201 Created
{"isi":"Belajar SQLModel","id":1}
```

Catatan kedua (`{"isi":"Tersimpan setelah restart"}`) mendapat `id` 2. `GET /catatan`:

```json
[{"isi":"Belajar SQLModel","id":1},{"isi":"Tersimpan setelah restart","id":2}]
```

### Bukti: data bertahan

Hentikan server (`Ctrl+C`), jalankan lagi dengan `fastapi dev main.py`, lalu:

```powershell
curl.exe http://127.0.0.1:8000/catatan
```

```json
[{"isi":"Belajar SQLModel","id":1},{"isi":"Tersimpan setelah restart","id":2}]
```

Data masih ada. Inilah perbedaan dengan penyimpanan di variabel Python.

### Temuan: model tabel tidak memvalidasi

Body kosong `{}` ke `POST /catatan`:

```text
HTTP/1.1 500 Internal Server Error
Internal Server Error
```

Bukan `422`. Log server mencatat `sqlalchemy.exc.IntegrityError: NOT NULL constraint failed: catatan.isi`. Artinya request lolos dari FastAPI, lalu basis data sendiri yang menolak karena `isi` wajib terisi. Pada pengujian ini, kelas dengan `table=True` yang dipakai langsung sebagai body tidak menghasilkan error validasi `422` seperti model Pydantic biasa. Cara memperbaikinya, yaitu memisahkan model untuk input dan model tabel, dibahas di halaman [Model dan Skema](model-dan-skema.md).

### Dokumentasi otomatis

Endpoint tampil di `/docs`. Tampilan visual Swagger UI **belum diverifikasi** lewat browser.

### Catatan: basis data lain dan sesi async

SQLite dipilih karena paling mudah dicoba. Untuk produksi, dokumentasi FastAPI menyarankan basis data server seperti PostgreSQL. Secara umum, yang berubah di kode hanyalah alamat dan driver pada `create_engine`; model, session, dan endpoint tetap sama. Bentuk alamatnya (dalam konvensi SQLAlchemy) kira-kira `postgresql+psycopg://pengguna:kata_sandi@host/nama_basis_data`. **Bagian ini tidak diuji**: periksa dokumentasi SQLAlchemy untuk driver dan versi yang kamu pakai, dan jangan menulis kata sandi langsung di kode (pengelolaan konfigurasi dan rahasia dibahas di Modul 08 dan 10).

Contoh di halaman ini memakai sesi **sinkron**. Versi dengan `await` dibahas di [Sesi Basis Data Async](sesi-async.md).

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Membuat engine di dalam fungsi endpoint | Engine baru untuk setiap request. Buat sekali di luar fungsi. |
| Lupa `commit()` | Perubahan tidak tersimpan. Tidak dijalankan di sini. |
| Lupa `refresh()` setelah `commit()` | `id` yang dibuat basis data mungkin tidak ikut terisi pada objek yang dikembalikan. Tidak dijalankan di sini. |
| Menjalankan server dari folder berbeda | `database.db` baru dibuat di folder itu, sehingga data lama tampak "hilang". Alamat `sqlite:///database.db` bersifat relatif terhadap folder kerja. |
| Memakai `@app.on_event("startup")` | Dinyatakan usang di dokumentasi FastAPI. Gunakan `lifespan`. |
| Mengirim `database.db` ke Git | Berisi data. Jangan di-commit. |
| Mengira `create_all` memperbarui tabel yang sudah ada | Hanya membuat tabel yang belum ada. Lihat [Migrasi](migrasi.md). |

## Latihan

1. **Dasar.** Hapus `database.db` lalu jalankan server. Apa isi `/db/tabel`? Mengapa?
2. **Persistensi.** Tambah dua catatan, hentikan server, jalankan lagi. Apa isi `GET /catatan`?
3. **Prediksi.** Apa yang terjadi bila `POST /catatan` dikirim `{}`? Apa penyebab sebenarnya?
4. **Analisis.** Mengapa session dibuat dengan dependency `yield`, bukan satu session global?

??? success "Kunci jawaban"
    Jawaban 1 dan 2 mengacu pada hasil uji di atas. Jawaban 4 adalah penalaran.

    1. `{"tabel":["catatan"]}`. Berkas dibuat ulang dan `create_all` membuat tabel `catatan` saat aplikasi mulai.
    2. Kedua catatan masih ada, dengan `id` 1 dan 2 (teruji).
    3. `500`, dengan `IntegrityError: NOT NULL constraint failed: catatan.isi` di log. Model tabel tidak memvalidasi body, sehingga basis data yang menolak (teruji).
    4. Satu session per request menjaga data tiap request tidak bercampur, dan dependency `yield` menutup session otomatis walau terjadi error, seperti pola pembersihan di Modul 05.

## Ringkasan

- Basis data menyimpan data di luar program sehingga bertahan setelah server mati.
- SQLModel dengan SQLite dipakai di modul ini; SQLite berupa satu berkas.
- **Engine** dibuat sekali; **session** dibuat per request lewat dependency `yield`.
- `lifespan` membuat tabel saat aplikasi mulai; `create_all` tidak mengubah tabel yang sudah ada.
- Tulis dengan `add` → `commit` → `refresh`; baca dengan `select`.
- Model tabel yang dipakai langsung sebagai body tidak menghasilkan `422`; ini diperbaiki dengan model terpisah.

## Langkah berikutnya

Lanjut ke [Model dan Skema](model-dan-skema.md), atau kembali ke daftar materi di [Modul 06: Basis Data](index.md).
