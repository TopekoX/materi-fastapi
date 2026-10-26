# Pengujian Async

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan kapan pengujian perlu berupa `async def`.
- [ ] Menulis pengujian async dengan `@pytest.mark.anyio` dan `httpx.AsyncClient`.
- [ ] Menyiapkan fixture async untuk sesi basis data async di memori.
- [ ] Memeriksa isi basis data langsung dengan `await` dari dalam pengujian.
- [ ] Menjalankan `lifespan` di pengujian async dengan `LifespanManager`.
- [ ] Mengenali jebakan: lupa marker, relasi yang tidak dimuat, dan `lifespan` yang tidak berjalan.

## Prasyarat

- Sudah membaca [Sesi Basis Data Async](../06-basis-data/sesi-async.md) dan [Basis Data untuk Pengujian](basis-data-pengujian.md).
- Sudah membaca [Fixture](fixture.md) dan [Override Dependency](override-dependency.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **SQLModel 0.0.48**, **aiosqlite 0.22.1**, **anyio 4.15.1**, **asgi-lifespan 2.1.0**, **pytest 9.1.1**, dan **httpx 0.28.1** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

### Kapan perlu pengujian async

Pengujian di halaman sebelumnya memakai `TestClient` dan fungsi `def` biasa. Itu cukup selama pengujian tidak perlu memanggil fungsi async. Menurut dokumentasi FastAPI, pengujian async berguna bila kode uji sendiri harus memanggil fungsi async, misalnya pustaka basis data async untuk memeriksa apakah request menulis data yang benar.

Aplikasi di [Sesi Basis Data Async](../06-basis-data/sesi-async.md) memakai `AsyncSession`. Memeriksa isinya dari pengujian berarti memakai `await`, sehingga pengujian harus `async def`.

### Alat yang dipakai

| Alat | Fungsi |
|---|---|
| **`@pytest.mark.anyio`** | Menandai pengujian agar dijalankan oleh plugin AnyIO (event loop) |
| **`httpx.AsyncClient`** | Klien HTTP async. Dipakai dengan `ASGITransport(app=app)` untuk memanggil aplikasi tanpa server |
| **`anyio_backend`** (fixture) | Menentukan backend async (`asyncio`) |
| **`asgi-lifespan`** | Menjalankan `lifespan` aplikasi di pengujian async (`LifespanManager`) |

Menurut dokumentasi FastAPI, `TestClient` dibangun di atas HTTPX; di dalam fungsi uji async, kamu memakai `AsyncClient` dengan `ASGITransport` secara langsung.

### Pemasangan

```powershell
pip install pytest asgi-lifespan aiosqlite greenlet
```

`anyio` dan `httpx` sudah terpasang bersama `fastapi[standard]` (teruji: terpasang di venv uji), dan plugin `anyio` terbaca otomatis oleh pytest.

## Kode lengkap

Contoh ada di `examples/fastapi/09-pengujian/pengujian-async/`.

### `main.py` (aplikasi yang diuji)

```python title="main.py"
--8<-- "fastapi/09-pengujian/pengujian-async/main.py"
```

Aplikasi sama polanya dengan halaman Sesi Basis Data Async: `AsyncSession`, `selectinload`, dan `lifespan`. `app.state.siap` hanya penanda bahwa `lifespan` sudah berjalan. Perhatikan skema `TugasBuat` yang membawa validasi (karena model tabel tidak memvalidasi masukan).

### `conftest.py`

```python title="conftest.py"
--8<-- "fastapi/09-pengujian/pengujian-async/conftest.py"
```

### `test_tugas_async.py`

```python title="test_tugas_async.py"
--8<-- "fastapi/09-pengujian/pengujian-async/test_tugas_async.py"
```

### `test_lifespan_async.py`

```python title="test_lifespan_async.py"
--8<-- "fastapi/09-pengujian/pengujian-async/test_lifespan_async.py"
```

## Penjelasan kode

### Menandai pengujian async

```python
pytestmark = pytest.mark.anyio
```

`pytestmark` di tingkat modul memberi marker `anyio` ke **semua** pengujian di berkas itu. Cara lain: tulis `@pytest.mark.anyio` di atas tiap fungsi (seperti pada dokumentasi FastAPI).

### Backend

```python
@pytest.fixture
def anyio_backend():
    return "asyncio"
```

Plugin AnyIO menjalankan pengujian pada backend yang ditentukan fixture ini. Kita membatasinya ke `asyncio`.

### Fixture async untuk basis data

```python
@pytest.fixture
async def session(anyio_backend):
    engine_uji = create_async_engine("sqlite+aiosqlite://", connect_args=..., poolclass=StaticPool)
    async with engine_uji.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with AsyncSession(engine_uji, expire_on_commit=False) as sesi:
        yield sesi
    await engine_uji.dispose()
```

Ini versi async dari fixture di [Basis Data untuk Pengujian](basis-data-pengujian.md): basis data memori baru per pengujian, dengan `StaticPool`. Fixture boleh `async def` dan memakai `yield`. Ia meminta `anyio_backend` agar plugin tahu backend yang dipakai. `create_all` dijalankan lewat `run_sync` karena tidak punya versi `await`, dan `dispose()` menutup engine di akhir.

### Fixture klien async

```python
@pytest.fixture
async def client(session):
    async def get_session_uji():
        yield session

    app.dependency_overrides[get_session] = get_session_uji
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as klien:
        yield klien
    app.dependency_overrides.clear()
```

`AsyncClient(transport=ASGITransport(app=app), base_url="http://test")` memanggil aplikasi langsung di dalam proses, tanpa server dan tanpa jaringan. `base_url` hanya awalan untuk path relatif. Override `get_session` memasang sesi uji (teknik dari [Override Dependency](override-dependency.md)).

### Memeriksa basis data dengan `await`

```python
hasil = await session.exec(select(Tugas))
assert [t.judul for t in hasil.all()] == ["Belajar pengujian async"]
```

Ini keuntungan utama pengujian async: pengujian dan aplikasi memakai **sesi yang sama**, dan pengujian bisa `await` langsung ke basis data untuk memastikan data benar-benar tersimpan, bukan hanya tampil di response.

### `lifespan` tidak dijalankan oleh `AsyncClient`

Menurut dokumentasi FastAPI, `AsyncClient` tidak memicu peristiwa `lifespan`; untuk itu dipakai `LifespanManager` dari `asgi-lifespan`:

```python
async with LifespanManager(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        ...
```

Pengujian kedua di `test_lifespan_async.py` juga memakai `monkeypatch.setattr(main, "engine", engine_uji)`. `lifespan` aplikasi membuat tabel di `main.engine`; dengan mengganti `engine` itu sementara dengan basis data memori, `database.db` tidak terbentuk. (`monkeypatch` dibahas di [Mock dan Monkeypatch](mock-monkeypatch.md).)

## Menjalankan

Dari folder contoh:

```powershell
pytest -v
```

Hasil sebenarnya:

```text
test_lifespan_async.py::test_asyncclient_tidak_menjalankan_lifespan PASSED
test_lifespan_async.py::test_dengan_lifespanmanager_lifespan_berjalan PASSED
test_tugas_async.py::test_buat_tugas PASSED
test_tugas_async.py::test_ambil_tugas_dengan_kategori PASSED
test_tugas_async.py::test_ambil_tugas_tidak_ada PASSED
test_tugas_async.py::test_validasi_judul PASSED
test_tugas_async.py::test_basis_data_baru_untuk_setiap_pengujian PASSED
============================== 7 passed ==============================
```

Berkas `database.db` tidak terbentuk setelahnya (teruji). Dua pengujian pertama membuktikan perilaku `lifespan`:

| Pengujian | Hasil |
|---|---|
| `AsyncClient` biasa, `GET /status` | `{"siap": false}` (`lifespan` tidak berjalan) |
| Dibungkus `LifespanManager`, `GET /status` | `{"siap": true}` |

Pengujian `test_ambil_tugas_dengan_kategori` menyiapkan kategori langsung lewat `session` (dengan `await`), membuat tugas lewat API, lalu memastikan response menyertakan nama kategori `"Kuliah"`.

### Jebakan yang teruji

**1. Lupa `@pytest.mark.anyio`.** Pengujian `async def` tanpa marker gagal:

```text
async def functions are not natively supported.
FAILED test_tanpa_marker.py::test_tanpa_marker - Failed: async def functions ...
```

Pytest sendiri tidak menjalankan fungsi async; plugin AnyIO yang melakukannya, dan hanya untuk yang bermarker.

**2. Relasi tidak dimuat di sesi uji.** Membaca `tugas.kategori` tanpa dimuat lebih dulu menghasilkan:

```text
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_() here. Was IO attempted in an unexpected place?
```

Sama seperti di [Sesi Basis Data Async](../06-basis-data/sesi-async.md): pada sesi async, relasi harus dimuat eksplisit (`selectinload`) atau di-`await`. Pengujian bisa tertipu bila hanya meniru kode aplikasi yang benar; kasus ini muncul bila pengujian sendiri membaca relasi.

**3. `TestClient` di dalam pengujian async.** Dokumentasi FastAPI menyebut `TestClient` tidak cocok dipakai di dalam fungsi uji async dan menganjurkan `AsyncClient`. Pada percobaan di sini, pemanggilan `TestClient(app).get("/status")` di dalam pengujian bermarker `anyio` ternyata **lolos** (`1 passed`). Jangan jadikan itu pegangan: memakai klien sinkron di dalam event loop yang sedang berjalan bertentangan dengan anjuran dokumentasi dan bisa gagal pada kode yang lebih rumit. Perilaku itu tidak diuji lebih jauh.

### Dokumentasi otomatis

Pengujian async tidak memengaruhi `/openapi.json`. Tampilan Swagger UI **belum diverifikasi** lewat browser.

## Kapan memilih sinkron, kapan async

| Situasi | Pilihan |
|---|---|
| Hanya mengirim request dan memeriksa response | `TestClient` sinkron, lebih sederhana |
| Perlu `await` ke basis data atau fungsi async dari pengujian | Pengujian async |
| Aplikasi memakai sesi async tetapi pengujian hanya lewat HTTP | `TestClient` tetap bisa dipakai (dokumentasi FastAPI: aplikasi async tetap bisa diuji dengan pengujian `def`). Tidak dijalankan di sini. |

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Lupa `@pytest.mark.anyio` | `async def functions are not natively supported` (teruji). |
| Tidak menyediakan fixture `anyio_backend` | Backend bawaan plugin yang dipakai; pada lingkungan dengan `trio` pengujian bisa dijalankan dua kali. Tidak diuji di sini. |
| Mengira `AsyncClient` menjalankan `lifespan` | Tidak; `app.state` kosong (teruji: `{"siap": false}`). Pakai `LifespanManager`. |
| Lupa `await` pada panggilan klien atau sesi | Pengujian membandingkan objek coroutine, bukan hasil. Tidak diuji di sini. |
| Menggunakan basis data produksi di pengujian async | Data nyata tercemar. Ganti `get_session` (teruji: `database.db` tidak terbentuk). |
| Mengarahkan basis data lewat `monkeypatch.chdir` | Pada percobaan di sini, `database.db` tetap terbentuk di folder kerja awal, jadi cara itu tidak dapat diandalkan. Ganti objek `engine` lewat `monkeypatch.setattr`. |
| Membuat objek yang butuh event loop di luar fungsi async | Dokumentasi FastAPI menyebut galat "Task attached to a different loop" pada kasus tertentu. Tidak diuji di sini. |

## Latihan

1. **Dasar.** Mengapa `test_buat_tugas` harus `async def`?
2. **Prediksi.** Apa hasil `GET /status` lewat `AsyncClient` biasa, dan lewat `LifespanManager`?
3. **Praktik.** Tulis pengujian async yang membuat dua tugas lalu memeriksa lewat `session` bahwa jumlahnya dua.
4. **Analisis.** Mengapa `StaticPool` tetap dibutuhkan pada engine async di memori?

??? success "Kunci jawaban"
    Jawaban 2 mengacu pada hasil uji di atas. Jawaban 3 adalah penerapan pola yang teruji dan tidak dijalankan. Jawaban 1 dan 4 adalah penalaran.

    1. Karena pengujian memakai `await` (pada `client.post(...)` dan pada `session.exec(...)`). `await` hanya boleh di dalam fungsi `async def`.
    2. Dengan `AsyncClient` biasa: `{"siap": false}`. Dengan `LifespanManager`: `{"siap": true}`.
    3. ```python
       async def test_dua_tugas(client, session):
           await client.post("/tugas", json={"judul": "Tugas satu"})
           await client.post("/tugas", json={"judul": "Tugas dua"})
           hasil = await session.exec(select(Tugas))
           assert len(hasil.all()) == 2
       ```
    4. Alasannya sama dengan versi sinkron: setiap koneksi baru ke `sqlite://` mendapat basis data memori yang kosong dan terpisah, sehingga `StaticPool` membuat semua koneksi memakai satu basis data yang sama. Kegagalan tanpa `StaticPool` pada versi sinkron teruji di halaman [Basis Data untuk Pengujian](basis-data-pengujian.md); pada versi async tidak diuji ulang.

## Ringkasan

- Pengujian async perlu bila pengujian harus memanggil fungsi async, misalnya `await` ke sesi basis data.
- Tandai dengan `@pytest.mark.anyio` (atau `pytestmark`), dan sediakan fixture `anyio_backend`.
- Panggil aplikasi dengan `AsyncClient(transport=ASGITransport(app=app), base_url=...)`.
- Fixture boleh `async def` dengan `yield`; basis data memori async memakai `StaticPool`.
- `AsyncClient` tidak menjalankan `lifespan`; pakai `LifespanManager`.
- Jebakan teruji: lupa marker gagal, relasi tanpa `selectinload` memunculkan `MissingGreenlet`.

## Langkah berikutnya

Lanjut ke [Mock dan Monkeypatch](mock-monkeypatch.md), atau kembali ke daftar materi di [Modul 09: Pengujian](index.md).
