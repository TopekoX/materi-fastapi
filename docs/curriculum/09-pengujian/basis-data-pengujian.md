# Basis Data untuk Pengujian

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan mengapa pengujian tidak boleh memakai basis data sungguhan.
- [ ] Menyiapkan basis data uji SQLite di memori dengan `StaticPool`.
- [ ] Mengganti `get_session` dengan sesi basis data uji lewat `dependency_overrides`.
- [ ] Menyiapkan basis data uji berupa berkas sementara dengan `tmp_path`.
- [ ] Menjamin setiap pengujian mulai dari basis data yang bersih.
- [ ] Menyiapkan data uji langsung lewat sesi, dan memeriksa isi basis data dari pengujian.
- [ ] Mengenali kesalahan umum: SQLite di memori tanpa `StaticPool`.

## Prasyarat

- Sudah membaca [Override Dependency](override-dependency.md) dan [Fixture](fixture.md).
- Sudah membaca [Operasi CRUD](../06-basis-data/operasi-crud.md) dan [Model dan Skema](../06-basis-data/model-dan-skema.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **SQLModel 0.0.48**, **SQLAlchemy 2.1.6**, dan **pytest 9.1.1** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Pengujian endpoint yang menyimpan data akan menulis ke basis data. Kalau pengujian memakai basis data yang sama dengan aplikasi (`database.db`), akibatnya:

- data uji bercampur dengan data sungguhan dan bisa merusaknya,
- hasil pengujian bergantung pada isi basis data sebelumnya,
- pengujian tidak bisa dijalankan berulang dengan hasil yang sama.

Prinsipnya: **basis data uji terpisah, dan baru untuk setiap pengujian**. Caranya memakai dua alat yang sudah kamu kenal: *fixture* untuk membuat dan membuang basis data, dan *override dependency* untuk memasangnya ke aplikasi.

Dua pilihan umum basis data uji pada SQLite:

| Pilihan | Cara | Catatan |
|---|---|---|
| **Di memori** | `create_engine("sqlite://", poolclass=StaticPool, ...)` | Tidak membuat berkas; hilang sendiri saat engine dilepas. Butuh `StaticPool`. |
| **Berkas sementara** | `create_engine(f"sqlite:///{tmp_path / 'uji.db'}")` | Memakai `tmp_path` dari pytest; berkas berada di folder sementara. |

Halaman ini memakai yang pertama sebagai utama, dan menunjukkan yang kedua sebagai alternatif.

## Kode lengkap

Contoh ada di `examples/fastapi/09-pengujian/basis-data-pengujian/`.

### `main.py` (aplikasi yang diuji)

```python title="main.py"
--8<-- "fastapi/09-pengujian/basis-data-pengujian/main.py"
```

`engine` di sini menunjuk `database.db`, yaitu basis data "produksi" yang tidak boleh disentuh pengujian. Perhatikan skema input `TugasBuat`; alasannya dijelaskan di bagian [pengujian yang menemukan bug](#pengujian-yang-menemukan-bug).

### `conftest.py` (basis data uji di memori)

```python title="conftest.py"
--8<-- "fastapi/09-pengujian/basis-data-pengujian/conftest.py"
```

### `test_tugas.py`

```python title="test_tugas.py"
--8<-- "fastapi/09-pengujian/basis-data-pengujian/test_tugas.py"
```

## Penjelasan kode

### Fixture `session`: basis data baru di memori

```python
engine_uji = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SQLModel.metadata.create_all(engine_uji)
with Session(engine_uji) as session:
    yield session
```

- `"sqlite://"` (tanpa nama berkas) berarti basis data SQLite **di memori**.
- `create_all` membuat semua tabel di basis data uji yang masih kosong.
- `yield session` menyerahkan sesi ke pengujian. Setelah pengujian selesai, `with` menutup sesi dan engine dilepas bersama basis data di memorinya, sehingga tidak ada yang perlu dihapus.
- Karena fixture ini berscope `function` (bawaan), **setiap pengujian mendapat basis data yang baru dan kosong**.

#### Mengapa `StaticPool`?

Di SQLite, setiap koneksi baru ke `sqlite://` mendapat basis data memori **sendiri dan kosong**. Aplikasi bisa memakai koneksi berbeda dari yang dipakai untuk membuat tabel (`TestClient` menjalankan aplikasi di *thread* lain). `StaticPool` membuat semua koneksi memakai satu koneksi yang sama sehingga semuanya melihat basis data yang sama. `check_same_thread=False` mengizinkan satu koneksi dipakai dari thread berbeda. Bukti kegagalannya ada di bagian jebakan di bawah.

### Fixture `client`: memasang basis data uji ke aplikasi

```python
def client_fixture(session: Session):
    def get_session_uji():
        yield session

    app.dependency_overrides[get_session] = get_session_uji
    with TestClient(app) as klien:
        yield klien
    app.dependency_overrides.clear()
```

`get_session` asli diganti dengan fungsi yang mengembalikan sesi uji (teknik dari halaman [Override Dependency](override-dependency.md)). Sesudah pengujian, override dilepas.

Dua fixture memakai `name=` pada `@pytest.fixture(name="session")`, agar nama fungsi (`session_fixture`) tidak bentrok dengan nama argumen (`session`) di pengujian.

### Memeriksa dan menyiapkan data langsung lewat sesi

Pengujian yang meminta `session` mendapat sesi yang **sama** dengan yang dipakai aplikasi, sehingga:

- **memeriksa isi**: `session.exec(select(Tugas)).all()` memastikan data benar-benar tersimpan, bukan hanya tampil di response;
- **menyiapkan data**: `session.add(Tugas(judul=...))` lalu `session.commit()` membuat data awal tanpa lewat endpoint `POST`. Cepat, dan pengujian `GET` tidak bergantung pada endpoint `POST`.

## Menjalankan

Dari folder contoh:

```powershell
pip install pytest sqlmodel
pytest -v
```

Hasil sebenarnya:

```text
test_tugas.py::test_buat_tugas PASSED
test_tugas.py::test_id_selalu_mulai_dari_satu PASSED
test_tugas.py::test_data_tidak_terbawa_antar_pengujian PASSED
test_tugas.py::test_filter_selesai PASSED
test_tugas.py::test_data_disiapkan_langsung_lewat_session PASSED
test_tugas.py::test_hapus_lalu_404 PASSED
test_tugas.py::test_validasi_judul PASSED
test_tugas.py::test_basis_data_produksi_tidak_tersentuh PASSED
============================== 8 passed ==============================
```

Beberapa pengujian menjawab kekhawatiran di awal:

| Pengujian | Yang dibuktikan |
|---|---|
| `test_id_selalu_mulai_dari_satu` | Basis data baru untuk setiap pengujian, sehingga `id` mulai dari 1 lagi. |
| `test_data_tidak_terbawa_antar_pengujian` | `GET /tugas` selalu `[]` di awal, tanpa sisa dari pengujian lain. |
| `test_basis_data_produksi_tidak_tersentuh` | Setelah membuat tugas, berkas `database.db` **tidak ada**: aplikasi memakai basis data uji, bukan yang produksi. |

### Alternatif: berkas sementara

`conftest_berkas_sementara.py` mengganti fixture `session`:

```python title="conftest_berkas_sementara.py"
--8<-- "fastapi/09-pengujian/basis-data-pengujian/conftest_berkas_sementara.py"
```

Basis datanya berupa berkas `uji.db` di `tmp_path`, folder sementara unik per pengujian. Bedanya dengan versi memori: ada berkas sungguhan (berguna bila ingin memeriksa berkasnya), dan `engine_uji.dispose()` perlu dipanggil agar koneksi tertutup (kamu akan menemukannya di komentar kode: penting di Windows agar berkas bisa dihapus). Dengan mengganti isi `conftest.py` dengan berkas ini, hasilnya sama: `8 passed`. Kecepatan keduanya tidak diukur.

### Pengujian yang menemukan bug

Pada percobaan pertama, `test_validasi_judul` **gagal**:

```text
E       assert 201 == 422
E        +  where 201 = <Response [201 Created]>.status_code
FAILED test_tugas.py::test_validasi_judul - assert 201 == 422
========================= 1 failed, 7 passed =========================
```

`POST /tugas` dengan judul `ab` (terlalu pendek) malah diterima. Penyebabnya adalah temuan yang sama dengan [Model dan Skema](../06-basis-data/model-dan-skema.md): versi pertama `main.py` memakai kelas tabel `Tugas` langsung sebagai body, dan kelas dengan `table=True` tidak memvalidasi masukan. Pengujian otomatis menangkap bug yang tidak terlihat bila hanya mencoba jalur sukses. Perbaikannya, yang kini ada di `main.py`: skema input `TugasBuat` yang membawa aturan validasi, lalu `Tugas.model_validate(data)`. Setelah itu kedelapan pengujian lolos.

(Percobaan itu dilakukan dengan versi lama `main.py` yang dijalankan terpisah; hasil di atas adalah keluaran sebenarnya.)

## Jebakan: SQLite di memori tanpa `StaticPool`

`conftest_salah.py` memakai `create_engine("sqlite://", connect_args=...)` tanpa `StaticPool`:

```python title="conftest_salah.py"
--8<-- "fastapi/09-pengujian/basis-data-pengujian/conftest_salah.py"
```

Hasil sebenarnya bila isi `conftest.py` diganti dengan berkas ini:

```text
E       sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: tugas
E       [SQL: INSERT INTO tugas (judul, selesai) VALUES (?, ?)]
FAILED test_tugas.py::test_buat_tugas - sqlalchemy.exc.OperationalError: ...
...
========================= 7 failed, 1 passed =========================
```

Tujuh pengujian gagal dengan `no such table: tugas`. Tabel sebenarnya dibuat oleh fixture, tetapi aplikasi berbicara lewat koneksi lain yang mendapat basis data memori kosong. (Pengujian yang tersisa, `test_validasi_judul`, lolos karena ditolak sebelum menyentuh basis data.) Pesan galat yang menyesatkan seperti ini alasan `StaticPool` perlu dipahami, bukan sekadar disalin.

### Migrasi Alembic untuk basis data uji

Cara lain menyiapkan skema uji adalah menjalankan migrasi Alembic pada basis data uji, sehingga skema uji identik dengan produksi. Cara itu **tidak diuji** di halaman ini. `SQLModel.metadata.create_all` mengikuti model, bukan berkas migrasi, jadi bila migrasi berbeda dari model, pengujian bisa lolos sementara basis data produksi bermasalah.

### Dokumentasi otomatis

Basis data uji tidak memengaruhi `/openapi.json`. Tampilan Swagger UI **belum diverifikasi** lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Menguji dengan `database.db` produksi | Data uji mencemari data sungguhan. Selalu ganti `get_session`. |
| SQLite di memori tanpa `StaticPool` | `no such table` (teruji: 7 dari 8 pengujian gagal). |
| Lupa melepas override di akhir fixture | Override bocor ke pengujian lain (lihat [Override Dependency](override-dependency.md)). |
| Basis data uji dipakai bersama antar pengujian (scope luas) tanpa membersihkan | Pengujian saling memengaruhi. Buat baru per pengujian, atau bersihkan. |
| Hanya menguji jalur sukses | Bug validasi tidak terlihat (teruji: `test_validasi_judul` menemukan bug). |
| Tidak memanggil `dispose()` pada engine berkas sementara di Windows | Berkas bisa tetap terkunci saat dihapus. Tidak diuji di sini. |
| Mengandalkan SQLite di memori untuk semua perilaku basis data | SQLite berbeda dari basis data server (misalnya PostgreSQL). Perilaku khusus basis data tertentu tidak teruji. |
| Menyalin `create_all` tanpa memikirkan migrasi | Skema uji bisa menyimpang dari skema produksi. |

## Latihan

1. **Dasar.** Mengapa `test_id_selalu_mulai_dari_satu` bisa selalu lolos?
2. **Prediksi.** Apa yang terjadi bila `poolclass=StaticPool` dihapus dari fixture?
3. **Praktik.** Tulis pengujian yang menyiapkan tiga tugas langsung lewat `session`, lalu memastikan `GET /tugas` mengembalikan tiga item.
4. **Analisis.** Mengapa lebih baik menyiapkan data awal lewat `session` daripada memanggil `POST` berkali-kali di pengujian `GET`?

??? success "Kunci jawaban"
    Jawaban 1 dan 2 mengacu pada hasil uji di atas. Jawaban 3 adalah penerapan pola yang teruji dan tidak dijalankan. Jawaban 4 adalah penalaran.

    1. Karena fixture `session` membuat basis data memori yang baru dan kosong untuk setiap pengujian, sehingga tabel `tugas` mulai dari kosong dan `id` pertama selalu `1`.
    2. Tujuh dari delapan pengujian gagal dengan `no such table: tugas` (hasil uji dengan `conftest_salah.py`).
    3. ```python
       def test_tiga_tugas(client, session):
           for judul in ("Satu", "Dua", "Tiga"):
               session.add(Tugas(judul=judul))
           session.commit()
           assert len(client.get("/tugas").json()) == 3
       ```
    4. Lebih cepat dan lebih terarah: pengujian `GET` tidak ikut gagal bila endpoint `POST` rusak, sehingga penyebab kegagalan lebih mudah ditemukan.

## Ringkasan

- Pengujian memakai basis data terpisah dan baru untuk setiap pengujian; jangan pernah menyentuh basis data produksi.
- SQLite di memori (`"sqlite://"`) membutuhkan `StaticPool` agar semua koneksi melihat basis data yang sama.
- Fixture `session` membuat basis data dan tabelnya; fixture `client` mengganti `get_session` lewat `dependency_overrides` dan melepasnya setelahnya.
- Sesi yang sama bisa dipakai pengujian untuk menyiapkan dan memeriksa data langsung.
- Alternatifnya basis data berupa berkas di `tmp_path`.
- Pengujian yang baik menemukan bug nyata, termasuk validasi yang terlewat.

## Langkah berikutnya

Lanjut ke [Pengujian Async](pengujian-async.md), atau kembali ke daftar materi di [Modul 09: Pengujian](index.md).
