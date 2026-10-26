# Fixture

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan apa itu fixture dan masalah yang dipecahkannya.
- [ ] Menulis fixture dengan `@pytest.fixture` dan memintanya lewat argumen pengujian.
- [ ] Menulis fixture dengan `yield` untuk persiapan dan pembersihan.
- [ ] Memakai `conftest.py` untuk berbagi fixture antar berkas.
- [ ] Memakai `autouse`, fixture yang memakai fixture lain, `scope`, dan `params`.
- [ ] Memakai `tmp_path` dan `@pytest.mark.parametrize`.
- [ ] Melihat urutan persiapan dan pembersihan dengan `--setup-show`.

## Prasyarat

- Sudah membaca [Pengujian Endpoint](pengujian-endpoint.md), terutama bagian jebakan pengujian yang saling bergantung.
- Sudah membaca [Dependency dengan yield](../05-dependency-injection/dependency-yield.md). Pola sebelum dan sesudah `yield` sama.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **pytest 9.1.1**, dan **httpx 0.28.1** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Di halaman sebelumnya, hampir setiap pengujian diawali `tugas_db.clear()`, dan satu pengujian gagal karena lupa membersihkan data. Persiapan yang diulang di mana-mana, dan mudah terlupa, adalah tanda perlunya **fixture**.

**Fixture** adalah fungsi yang menyiapkan sesuatu yang dibutuhkan pengujian (data, klien, berkas sementara), dan boleh membersihkannya sesudahnya. Pengujian "meminta" fixture dengan menulis namanya sebagai argumen, lalu pytest menjalankan fixture itu dan memberikan hasilnya. Menurut dokumentasi pytest, fixture dibuat dengan dekorator `@pytest.fixture`.

```python
@pytest.fixture
def header_token():
    return {"X-Token": TOKEN_RAHASIA}


def test_hapus(client, header_token):   # pytest menyuplai kedua argumen
    ...
```

## Kode lengkap

Contoh ada di `examples/fastapi/09-pengujian/fixture/`. Aplikasi `main.py` sama dengan halaman sebelumnya, ditambah fungsi kecil `simpan_ringkasan` untuk demonstrasi `tmp_path`.

### `conftest.py` (fixture bersama)

```python title="conftest.py"
--8<-- "fastapi/09-pengujian/fixture/conftest.py"
```

### `test_tugas.py` (pengujian)

```python title="test_tugas.py"
--8<-- "fastapi/09-pengujian/fixture/test_tugas.py"
```

### `test_urutan_bebas.py` dan `test_scope.py`

```python title="test_urutan_bebas.py"
--8<-- "fastapi/09-pengujian/fixture/test_urutan_bebas.py"
```

```python title="test_scope.py"
--8<-- "fastapi/09-pengujian/fixture/test_scope.py"
```

## Penjelasan kode

### `conftest.py`: tempat fixture bersama

Berkas bernama `conftest.py` dibaca pytest secara otomatis. Fixture di dalamnya tersedia untuk semua pengujian di folder itu, tanpa perlu `import` (dokumentasi pytest).

### Fixture autouse: membersihkan data

```python
@pytest.fixture(autouse=True)
def data_bersih():
    tugas_db.clear()
    yield
    tugas_db.clear()
```

- `autouse=True`: dijalankan untuk **setiap** pengujian tanpa perlu diminta. Inilah pengganti `tugas_db.clear()` di tiap tes.
- `yield` memisahkan **persiapan** (sebelum) dan **pembersihan** (sesudah). Pembersihan tetap dijalankan sekalipun pengujiannya gagal. Menurut dokumentasi pytest, bila fixture melempar exception *sebelum* `yield`, pembersihan fixture itu tidak dijalankan.

### Fixture klien

```python
@pytest.fixture
def client():
    with TestClient(app) as klien:
        yield klien
```

Memakai `with TestClient(app)` agar `lifespan` ikut berjalan (lihat [Lifespan](../08-struktur-proyek/lifespan.md)). Aplikasi ini tidak punya `lifespan`, tetapi kebiasaan ini aman dan perlu untuk aplikasi yang punya.

### Fixture yang memakai fixture lain

```python
@pytest.fixture
def tugas_contoh(client):
    response = client.post("/tugas", json={"judul": "Tugas contoh"})
    return response.json()
```

`tugas_contoh` meminta `client`. Pengujian yang meminta `tugas_contoh` mendapat tugas yang sudah dibuat, tanpa menulis langkah pembuatannya. Dalam satu pengujian, tiap fixture hanya dijalankan sekali dan hasilnya dipakai bersama (dokumentasi pytest).

### Fixture berparameter

```python
@pytest.fixture(params=["Belajar", "Menulis kode", "Membaca dokumentasi"])
def judul_valid(request):
    return request.param
```

Setiap pengujian yang memakai `judul_valid` dijalankan **sekali per nilai** di `params`. Nilai saat ini dibaca dari `request.param`.

### `parametrize`: beberapa kasus, satu pengujian

```python
@pytest.mark.parametrize(
    "judul, status_diharapkan",
    [("abc", 201), ("ab", 422), ("", 422), ("x" * 100, 201), ("x" * 101, 422)],
)
def test_batas_panjang_judul(client, judul, status_diharapkan):
```

Satu fungsi dijalankan untuk setiap baris data. Cocok untuk menguji nilai-nilai batas. Di contoh ini, panjang 3 dan 100 diterima, sedangkan 2, 0, dan 101 ditolak.

### `tmp_path`: folder sementara bawaan pytest

```python
def test_simpan_ringkasan(tmp_path, client):
    ...
    jalur = simpan_ringkasan(tmp_path, list(tugas_db.values()))
```

`tmp_path` adalah fixture bawaan pytest yang memberi folder sementara yang unik per pengujian. Cocok untuk menguji kode yang menulis berkas tanpa mengotori proyek.

### `scope`: seberapa lama fixture hidup

Menurut dokumentasi pytest, `scope` menentukan masa hidup fixture:

| `scope` | Dihancurkan |
|---|---|
| `function` (bawaan) | setelah setiap pengujian |
| `class` | setelah pengujian terakhir di kelas |
| `module` | setelah pengujian terakhir di berkas |
| `package` | setelah pengujian terakhir di paket |
| `session` | di akhir seluruh sesi pengujian |

`test_scope.py` membuktikannya. `per_fungsi` dibuat ulang untuk tiap pengujian, sedangkan `per_modul` dibuat sekali. Fixture berscope luas menghemat waktu bila persiapannya mahal (misalnya membuat basis data), tetapi berisiko membuat pengujian saling bergantung lagi: pakai hanya untuk sumber daya yang tidak diubah pengujian.

## Menjalankan

Dari folder contoh:

```powershell
pytest
```

Hasil sebenarnya (`pytest -v`, dipersingkat; 17 pengujian di empat berkas):

```text
test_tugas.py::test_daftar_awal_kosong PASSED
test_tugas.py::test_buat_tugas PASSED
test_tugas.py::test_ambil_tugas_contoh PASSED
test_tugas.py::test_hapus_tugas_contoh PASSED
test_tugas.py::test_judul_valid_diterima[Belajar] PASSED
test_tugas.py::test_judul_valid_diterima[Menulis kode] PASSED
test_tugas.py::test_judul_valid_diterima[Membaca dokumentasi] PASSED
test_tugas.py::test_batas_panjang_judul[abc-201] PASSED
test_tugas.py::test_batas_panjang_judul[ab-422] PASSED
test_tugas.py::test_batas_panjang_judul[-422] PASSED
  ... (dua kasus panjang 100 dan 101)
test_tugas.py::test_simpan_ringkasan PASSED
test_urutan_bebas.py::test_a_membuat_tugas PASSED
test_urutan_bebas.py::test_b_daftar_kosong PASSED
test_scope.py::... (2 pengujian)
============================== 17 passed ==============================
```

Perhatikan nama di dalam tanda kurung (`[Belajar]`, `[ab-422]`): satu fungsi, banyak kasus. Tanpa `autouse`, `test_buat_tugas` yang mengharapkan `id` selalu `1` akan bergantung pada urutan.

### Melihat urutan persiapan dan pembersihan

`--setup-show` memperlihatkan kapan fixture dibuat (`SETUP`) dan dibersihkan (`TEARDOWN`). `F` berarti scope `function`, `M` berarti `module`:

```powershell
pytest "test_tugas.py::test_ambil_tugas_contoh" --setup-show
```

```text
        SETUP    F data_bersih
        SETUP    F client
        SETUP    F tugas_contoh (fixtures used: client)
        test_tugas.py::test_ambil_tugas_contoh (fixtures used: client, data_bersih, tugas_contoh) .
        TEARDOWN F tugas_contoh
        TEARDOWN F client
        TEARDOWN F data_bersih
```

Urutan pembersihan **terbalik** dari urutan persiapan, sama seperti dependency `yield` berantai di Modul 05.

Untuk `test_scope.py`:

```text
    SETUP    M per_modul
        SETUP    F per_fungsi
        test_scope.py::test_pertama ...
        TEARDOWN F per_fungsi
        SETUP    F per_fungsi
        test_scope.py::test_kedua ...
        TEARDOWN F per_fungsi
    TEARDOWN M per_modul
```

`per_modul` (scope `M`) dibuat sekali di awal dan dihancurkan di akhir, sedangkan `per_fungsi` dibuat dan dihancurkan untuk tiap pengujian. (Output asli juga memuat `data_bersih` di setiap pengujian; dihilangkan di sini agar ringkas.)

### Pengujian lolos dalam urutan apa pun

`test_urutan_bebas.py` adalah versi perbaikan dari masalah di halaman sebelumnya. Dijalankan dengan `test_b` lebih dulu lalu `test_a`, keduanya lolos:

```text
test_urutan_bebas.py::test_b_daftar_kosong PASSED
test_urutan_bebas.py::test_a_membuat_tugas PASSED
```

Bila `conftest.py` diganti sehingga fixture `data_bersih` dihilangkan (hanya fixture `client` yang tersisa), `test_a` lalu `test_b` kembali bermasalah:

```text
test_urutan_bebas.py::test_a_membuat_tugas PASSED
test_urutan_bebas.py::test_b_daftar_kosong FAILED
========================= 1 failed, 1 passed =========================
```

Jadi kebersihan data memang datang dari fixture `autouse`, bukan dari kebetulan urutan.

### Daftar fixture

`pytest --fixtures` menampilkan semua fixture yang tersedia, termasuk yang bawaan (seperti `tmp_path`) dan yang kamu buat (`client`, `header_token`, `tugas_contoh`, `judul_valid`, `data_bersih`), beserta lokasi definisinya.

### Dokumentasi otomatis

Fixture tidak memengaruhi `/openapi.json`. Tampilan Swagger UI **belum diverifikasi** lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Fixture lupa `yield` atau `return` | Pengujian menerima `None`. Tidak diuji di sini. |
| Fixture `autouse` yang tidak membersihkan | Data bocor ke pengujian lain (teruji: tanpa `data_bersih`, `test_b` gagal). |
| Memakai `scope="session"` untuk sumber daya yang diubah pengujian | Pengujian saling memengaruhi lagi. |
| Menaruh fixture bersama di berkas tes yang diimpor manual | Pakai `conftest.py`; tidak perlu impor. |
| Mengira pembersihan jalan bila persiapan gagal | Bila exception terjadi sebelum `yield`, pembersihan fixture itu tidak dijalankan (dokumentasi pytest). Tidak diuji. |
| Fixture berparameter tanpa `request` | `request.param` tidak terbaca. Tidak diuji. |
| Terlalu banyak fixture `autouse` | Setiap pengujian ikut membayar biayanya. Pakai hanya untuk yang benar-benar dibutuhkan semua. |
| Mengubah data hasil fixture berscope luas | Perubahan terlihat oleh pengujian lain. |

## Latihan

1. **Dasar.** Fixture mana yang membuat `test_buat_tugas` selalu mendapat `id` bernilai `1`?
2. **Prediksi.** Berapa kali `per_modul` dibuat di `test_scope.py`? Berapa kali `per_fungsi`?
3. **Praktik.** Tambahkan fixture `dua_tugas` yang membuat dua tugas lewat `client`, lalu tulis pengujian bahwa `GET /tugas` mengembalikan dua item.
4. **Analisis.** Mengapa urutan `TEARDOWN` terbalik dari `SETUP`?

??? success "Kunci jawaban"
    Jawaban 1 dan 2 mengacu pada hasil uji di atas. Jawaban 3 adalah penerapan pola yang teruji dan tidak dijalankan. Jawaban 4 adalah penalaran.

    1. `data_bersih` (autouse): mengosongkan `tugas_db` sebelum setiap pengujian.
    2. `per_modul`: sekali. `per_fungsi`: dua kali, satu per pengujian (hasil `--setup-show`).
    3. ```python
       @pytest.fixture
       def dua_tugas(client):
           client.post("/tugas", json={"judul": "Tugas satu"})
           client.post("/tugas", json={"judul": "Tugas dua"})


       def test_daftar_dua_tugas(client, dua_tugas):
           assert len(client.get("/tugas").json()) == 2
       ```
    4. Fixture yang dibuat belakangan mungkin bergantung pada yang dibuat lebih dulu (`tugas_contoh` memakai `client`). Membersihkan dalam urutan terbalik memastikan sesuatu tidak dihancurkan selagi masih dipakai oleh yang lain.

## Ringkasan

- Fixture adalah fungsi yang menyiapkan (dan membersihkan) sesuatu untuk pengujian; pengujian memintanya lewat nama argumen.
- `yield` dalam fixture memisahkan persiapan dan pembersihan; pembersihan berjalan terbalik dari persiapan.
- `conftest.py` membagikan fixture ke semua pengujian di foldernya.
- `autouse=True` menjalankan fixture untuk setiap pengujian, cocok untuk membersihkan data.
- `scope` mengatur masa hidup fixture; `params` dan `@pytest.mark.parametrize` menjalankan satu pengujian untuk banyak nilai.
- `tmp_path` memberi folder sementara; `--setup-show` memperlihatkan urutan fixture.

## Langkah berikutnya

Lanjut ke [Override Dependency](override-dependency.md), atau kembali ke daftar materi di [Modul 09: Pengujian](index.md).
