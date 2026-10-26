# Sesi Basis Data Async

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan kapan sesi async berguna dan apa bedanya dengan sesi sinkron.
- [ ] Membuat engine async (`create_async_engine`) dan `AsyncSession` dengan SQLModel.
- [ ] Membuat tabel di engine async dengan `run_sync`.
- [ ] Menulis endpoint `async def` yang memakai `await` pada operasi basis data.
- [ ] Menghindari error `MissingGreenlet` dengan memuat relasi lewat `selectinload`.
- [ ] Menjelaskan fungsi `expire_on_commit=False`.

## Prasyarat

- Sudah membaca [Operasi CRUD](operasi-crud.md) dan [Relasi](relasi.md).
- Sudah membaca [Dasar Async/Await](../02-dasar-routing/async-await.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **SQLModel 0.0.48**, **SQLAlchemy 2.1.6**, **aiosqlite 0.22.1**, dan **greenlet 3.5.6** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Di [Dasar Async/Await](../02-dasar-routing/async-await.md) kamu melihat bahwa endpoint `async def` yang menunggu hal lambat (seperti jaringan atau basis data) bisa melepaskan server untuk melayani request lain selama menunggu, asalkan menunggunya memakai `await`. Sesi sinkron yang kita pakai di halaman-halaman sebelumnya **memblokir** saat kueri berjalan. Sesi **async** memungkinkan `await` pada setiap operasi basis data.

Kapan perlu memilih async? Pertimbangannya:

| Pertimbangan | Sinkron | Async |
|---|---|---|
| Kesederhanaan | Lebih sederhana | Perlu `await` di mana-mana |
| Relasi | Dimuat otomatis saat diakses | **Harus dimuat eksplisit** (lihat di bawah) |
| Library | `sqlmodel` saja | Tambahan driver async dan `greenlet` |
| Aplikasi | Cocok untuk kebanyakan kebutuhan awal | Cocok bila banyak request menunggu basis data bersamaan |

Halaman ini tidak mengukur kinerja kedua pendekatan, jadi tidak ada klaim bahwa async selalu lebih cepat. Untuk SQLite di satu berkas, keuntungannya bisa kecil; contoh ini bertujuan menunjukkan **cara**, dan polanya sama untuk basis data server seperti PostgreSQL.

### Pemasangan

Selain SQLModel, sesi async membutuhkan driver async untuk SQLite (`aiosqlite`) dan `greenlet`. Dokumentasi SQLAlchemy menyarankan `pip install sqlalchemy[asyncio]` agar `greenlet` ikut terpasang. Dengan venv aktif:

```powershell
pip install sqlmodel aiosqlite greenlet
```

Tanpa `greenlet`, mengimpor `sqlmodel.ext.asyncio.session` gagal dengan `ImportError: The SQLAlchemy asyncio module requires that the Python 'greenlet' library is installed` (teruji).

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/06-basis-data/sesi-async/main.py"
```

## Penjelasan kode

### Engine async

```python
engine = create_async_engine("sqlite+aiosqlite:///database.db")
```

Dibandingkan `create_engine("sqlite:///database.db")`, alamatnya memakai `sqlite+aiosqlite`, yaitu SQLite lewat driver async `aiosqlite`. Pengaturan `check_same_thread` tidak lagi dipakai di contoh ini.

### Membuat tabel dan menutup engine

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    await engine.dispose()
```

- `create_all` tidak punya versi `await`, sehingga dijalankan lewat `conn.run_sync(...)` pada koneksi dari `engine.begin()`. Pola ini ada di dokumentasi SQLAlchemy.
- `await engine.dispose()` setelah `yield` menutup koneksi saat aplikasi berhenti. Dokumentasi SQLAlchemy menekankan engine async perlu di-`dispose` secara eksplisit.

### Session async

```python
async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
```

Ini dependency `yield` berbentuk `async def` ([Dependency dengan yield](../05-dependency-injection/dependency-yield.md)). `AsyncSession` dari `sqlmodel.ext.asyncio.session` adalah versi async dari `Session`, dan tetap punya `.exec(...)`.

`expire_on_commit=False` penting. Secara bawaan, setelah `commit` semua atribut objek ditandai kedaluwarsa dan dimuat ulang saat dibaca, dan pemuatan ulang itu membutuhkan akses basis data yang tidak boleh terjadi diam-diam pada async. Hasil uji di bawah menunjukkan akibatnya.

### Endpoint dengan `await`

```python
@app.post("/tugas", status_code=201)
async def buat_tugas(judul: str, session: SessionDep, kategori_id: int | None = None):
    tugas = Tugas(judul=judul, kategori_id=kategori_id)
    session.add(tugas)
    await session.commit()
    await session.refresh(tugas)
    return tugas
```

- `session.add` tetap tanpa `await` (hanya mendaftarkan objek).
- `commit` dan `refresh` menyentuh basis data, jadi memakai `await`.

```python
hasil = await session.exec(select(Tugas))
return hasil.all()
```

`await session.exec(...)` menjalankan kueri; hasilnya dibaca dengan `.all()` seperti biasa.

Contoh ini memakai model tabel langsung dan parameter query demi singkat. Di kode nyata, pakai skema terpisah seperti di [Model dan Skema](model-dan-skema.md).

### Memuat relasi dengan `selectinload`

```python
pernyataan = select(Tugas).where(Tugas.id == tugas_id).options(selectinload(Tugas.kategori))
tugas = (await session.exec(pernyataan)).first()
```

`selectinload(Tugas.kategori)` meminta kategori dimuat **bersama** kueri tugas. Dengan begitu `tugas.kategori` sudah terisi saat dibaca. Pada async, relasi tidak boleh dimuat diam-diam saat diakses.

Endpoint `/tugas/{id}/salah` sengaja membaca `tugas.kategori` tanpa memuatnya, untuk membuktikan masalahnya.

## Menjalankan

```powershell
pip install sqlmodel aiosqlite greenlet
fastapi dev main.py
```

Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah. Berkas `database.db` dibuat di folder kerja.

## Mencoba request

Hasil di bawah dijalankan berurutan dengan `curl.exe` dari keadaan tanpa `database.db`.

| Request | Status | Isi |
|---|---|---|
| `POST /kategori?nama=Kuliah` | `201` | `{"id":1,"nama":"Kuliah"}` |
| `POST /tugas?judul=Belajar async&kategori_id=1` | `201` | `{"selesai":false,"judul":"Belajar async","kategori_id":1,"id":1}` |
| `POST /tugas?judul=Tanpa kategori` | `201` | tugas `id` 2, `"kategori_id":null` |
| `GET /tugas` | `200` | kedua tugas |
| `GET /tugas/1` | `200` | `{"id":1,"judul":"Belajar async","kategori":"Kuliah"}` |
| `GET /tugas/2` | `200` | `{"id":2,"judul":"Tanpa kategori","kategori":null}` |
| `GET /tugas/99` | `404` | `{"detail":"Tugas tidak ditemukan"}` |

(Spasi pada `judul` dikirim sebagai `%20` di URL.)

### Temuan: `MissingGreenlet`

```text
GET /tugas/1/salah  ->  HTTP/1.1 500 Internal Server Error
```

Log server mencatat:

```text
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_() here. Was IO attempted in an unexpected place?
```

Membaca `tugas.kategori` tanpa memuatnya mencoba menjalankan kueri di tempat yang tidak boleh, sehingga SQLAlchemy melaporkan `MissingGreenlet`. Pada sesi sinkron, relasi yang sama dimuat otomatis tanpa error (seperti di [Relasi](relasi.md)). Pada async, muat relasi secara eksplisit.

### Temuan: `expire_on_commit`

Diuji dengan skrip terpisah yang menyimpan satu objek lalu membaca `it.nama` setelah `commit` tanpa `refresh`:

| `expire_on_commit` | Hasil membaca atribut setelah `commit` |
|---|---|
| `True` (bawaan) | `StatementError` |
| `False` | `a` (nilai terbaca) |

Karena itu `get_session` memakai `expire_on_commit=False`.

Skrip yang sama juga membuktikan filter dan hapus berjalan secara async: `await session.exec(select(Item).where(Item.nama == "a"))` mengembalikan baris yang cocok, dan `await session.delete(objek)` diikuti `await session.commit()` menghapusnya.

### Dokumentasi otomatis

Endpoint `async def` tampil di `/docs` seperti biasa. Tampilan visual Swagger UI **belum diverifikasi** lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Lupa `await` pada `commit`, `refresh`, atau `exec` | Fungsi async yang tidak di-`await` hanya menghasilkan objek *coroutine* dan tidak dijalankan; Python biasanya memberi peringatan *coroutine was never awaited*. Tidak diuji pada contoh ini. |
| Membaca relasi tanpa `selectinload` | `500` dan `MissingGreenlet` (teruji). |
| Tidak memakai `expire_on_commit=False` | Membaca atribut setelah `commit` menghasilkan `StatementError` (teruji). |
| Lupa memasang `greenlet` atau `aiosqlite` | `ImportError` untuk `greenlet` (teruji); untuk `aiosqlite`, kegagalan tidak diuji. |
| Memakai engine sinkron dengan `AsyncSession` | Tidak cocok. Pakai `create_async_engine`. Tidak dijalankan di sini. |
| Memakai satu `AsyncSession` untuk beberapa tugas bersamaan | Dokumentasi SQLAlchemy menyatakan tidak aman; pakai satu session per tugas. Tidak diuji. |
| Lupa `await engine.dispose()` | Dokumentasi SQLAlchemy mengingatkan pembuangan engine async harus eksplisit. |

## Latihan

1. **Dasar.** Apa perbedaan alamat engine sinkron dan async untuk SQLite?
2. **Prediksi.** Apa status dan error untuk `GET /tugas/1/salah`? Bagaimana memperbaikinya?
3. **Praktik.** Tambahkan filter `selesai` pada `GET /tugas` versi async. Bagaimana kueri dibentuk?
4. **Analisis.** Mengapa `create_all` dijalankan lewat `run_sync`?

??? success "Kunci jawaban"
    Jawaban 2 mengacu pada hasil uji di atas. Jawaban 3 adalah penalaran yang mengikuti pola yang teruji pada skrip (`select(...).where(...)`). Jawaban 1 dan 4 adalah penalaran.

    1. Sinkron: `sqlite:///database.db`. Async: `sqlite+aiosqlite:///database.db`, dibuat dengan `create_async_engine`.
    2. `500` dengan `MissingGreenlet`. Perbaiki dengan `.options(selectinload(Tugas.kategori))` pada kueri, seperti endpoint `/tugas/{id}`.
    3. Tambahkan parameter `selesai: bool | None = None`, bentuk `pernyataan = select(Tugas)`, tambahkan `.where(Tugas.selesai == selesai)` bila parameter diisi, lalu `hasil = await session.exec(pernyataan)` dan `hasil.all()`.
    4. `create_all` adalah fungsi sinkron tanpa `await`. `run_sync` menjalankannya di dalam koneksi async.

## Ringkasan

- Sesi async memungkinkan `await` pada operasi basis data; pilih bila banyak request menunggu basis data bersamaan.
- Butuh `create_async_engine` dengan alamat `sqlite+aiosqlite://`, `AsyncSession`, serta paket `aiosqlite` dan `greenlet`.
- Buat tabel lewat `conn.run_sync(SQLModel.metadata.create_all)`, dan tutup engine dengan `await engine.dispose()`.
- Pakai `expire_on_commit=False` agar atribut tetap terbaca setelah `commit`.
- Muat relasi secara eksplisit dengan `selectinload`; tanpa itu muncul `MissingGreenlet`.
- Tambahkan `await` pada `commit`, `refresh`, dan `exec`; `add` tanpa `await`.

## Langkah berikutnya

Lanjut ke [Migrasi](migrasi.md), atau kembali ke daftar materi di [Modul 06: Basis Data](index.md).
