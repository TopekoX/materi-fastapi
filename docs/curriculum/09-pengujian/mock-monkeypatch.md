# Mock dan Monkeypatch

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan kapan override dependency tidak cukup dan kapan `monkeypatch` atau `mock` dibutuhkan.
- [ ] Mengganti fungsi sementara dengan `monkeypatch.setattr`.
- [ ] Mengganti waktu dan variabel environment saat pengujian.
- [ ] Memakai `unittest.mock.Mock` untuk merekam pemanggilan dan mensimulasikan kegagalan.
- [ ] Menentukan **tempat yang benar** untuk mengganti sesuatu.
- [ ] Menjelaskan bahwa penggantian dibatalkan otomatis.

## Prasyarat

- Sudah membaca [Override Dependency](override-dependency.md) dan [Fixture](fixture.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **pytest 9.1.1**, dan **httpx 0.28.1** di Windows. `unittest.mock` adalah bagian dari pustaka standar Python. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Di [Override Dependency](override-dependency.md) kita mengganti sesuatu yang dipasang lewat `Depends`. Tetapi tidak semua yang ingin diganti berupa dependency:

- fungsi yang dipanggil langsung di dalam endpoint (misalnya memanggil layanan luar),
- **waktu sekarang** (`datetime.now()`), yang berubah terus,
- **variabel environment**,
- fungsi dari pustaka lain.

Untuk itu pytest menyediakan fixture `monkeypatch`, dan pustaka standar Python menyediakan `unittest.mock`.

| Alat | Cocok untuk |
|---|---|
| `app.dependency_overrides` | Sesuatu yang dipasang lewat `Depends` |
| **`monkeypatch`** | Mengganti atribut modul, nilai `dict`, atau variabel environment selama satu pengujian |
| **`unittest.mock.Mock`** | Pengganti yang **merekam pemanggilan** (berapa kali, dengan argumen apa) atau **melempar kegagalan** sesuai keinginan |

Menurut dokumentasi pytest, `monkeypatch` mengubah atribut, item `dict`, variabel environment, `sys.path`, atau direktori kerja secara sementara, dan **semua perubahan dibatalkan otomatis** setelah pengujian atau fixture yang memintanya selesai.

Aturan umum: gunakan override dependency bila ada dependency, dan `monkeypatch` atau `mock` bila tidak.

## Kode lengkap

Contoh ada di `examples/fastapi/09-pengujian/mock-monkeypatch/`.

### `layanan.py` (layanan luar)

```python title="layanan.py"
--8<-- "fastapi/09-pengujian/mock-monkeypatch/layanan.py"
```

Alamatnya memakai domain `.invalid`, yang memang tidak pernah ada, sehingga pemanggilan ini selalu gagal.

### `main.py` (aplikasi yang diuji)

```python title="main.py"
--8<-- "fastapi/09-pengujian/mock-monkeypatch/main.py"
```

Endpoint `/kurs` memanggil `ambil_kurs()` langsung (bukan lewat `Depends`), `/salam` bergantung pada waktu sekarang, dan `/mode` membaca variabel environment saat dipanggil.

### `test_monkeypatch.py`

```python title="test_monkeypatch.py"
--8<-- "fastapi/09-pengujian/mock-monkeypatch/test_monkeypatch.py"
```

### `test_mock.py`

```python title="test_mock.py"
--8<-- "fastapi/09-pengujian/mock-monkeypatch/test_mock.py"
```

## Penjelasan kode

### `monkeypatch.setattr`: mengganti fungsi

```python
def test_kurs_dengan_fungsi_pengganti(monkeypatch):
    monkeypatch.setattr(main, "ambil_kurs", lambda: 16000.0)
    response = client.get("/kurs", params={"jumlah": 2})
    assert response.json() == {"jumlah": 2.0, "kurs": 16000.0, "hasil": 32000.0}
```

`monkeypatch` adalah fixture bawaan pytest; cukup disebut sebagai argumen. `setattr(objek, "nama", nilai)` mengganti atribut `nama` pada `objek` (di sini modul `main`) selama pengujian ini. Setelah pengujian selesai, aslinya dikembalikan.

### Penting: ganti di tempat nama itu **dipakai**

```python
# main.py
from layanan import ambil_kurs
```

Baris ini menyalin nama `ambil_kurs` ke modul `main`. Maka `main.ambil_kurs` dan `layanan.ambil_kurs` adalah dua nama yang menunjuk fungsi yang sama. Fungsi `konversi` memakai `main.ambil_kurs`, jadi **itulah yang harus diganti**:

```python
monkeypatch.setattr(layanan, "ambil_kurs", lambda: 16000.0)   # salah tempat
```

`test_salah_tempat_penggantian_tidak_berefek` membuktikannya: mengganti `layanan.ambil_kurs` tidak mengubah apa yang dipakai `main`, sehingga request tetap memanggil layanan asli dan menghasilkan `503`. Ini jebakan paling umum pada penggantian: **ganti nama di modul yang memakainya, bukan di modul asalnya**.

### Mengganti waktu

```python
monkeypatch.setattr(main, "waktu_sekarang", lambda: datetime(2026, 1, 1, jam, 0))
```

Karena endpoint memanggil fungsi `waktu_sekarang()` (bukan `datetime.now()` langsung), kita punya titik penggantian yang jelas. Perancangan seperti itu, yaitu membungkus hal yang tidak dapat diprediksi dalam fungsi kecil, membuat kode mudah diuji. Pengujian berparameter memeriksa empat sapaan pada empat jam.

### Mengganti variabel environment

```python
monkeypatch.setenv("TUGASKU_MODE", "uji")
monkeypatch.delenv("TUGASKU_MODE", raising=False)
```

`setenv` mengisi variabel selama pengujian, `delenv` menghapusnya (`raising=False` agar tidak error bila variabelnya memang belum ada). Endpoint `/mode` membaca `os.environ` **saat dipanggil**; bila dibaca saat impor modul, penggantian di dalam pengujian terlambat.

### `unittest.mock.Mock`: merekam dan mensimulasikan

```python
pengganti = Mock(return_value=15000.0)
with patch.object(main, "ambil_kurs", pengganti):
    response = client.get("/kurs", params={"jumlah": 10})
pengganti.assert_called_once_with()
```

- `Mock(return_value=...)` adalah objek yang bisa dipanggil seperti fungsi dan mengembalikan nilai tertentu.
- `patch.object(main, "ambil_kurs", pengganti)` mengganti atribut hanya di dalam blok `with`, lalu mengembalikannya. Fungsinya mirip `monkeypatch.setattr`.
- `assert_called_once_with()` memastikan fungsi dipanggil **tepat sekali** dan dengan argumen tertentu (di sini tanpa argumen). Itu bukti yang tidak terlihat dari response.
- `assert_not_called()` memastikan fungsi **tidak** dipanggil: pada `test_mock_tidak_dipanggil_bila_validasi_gagal`, validasi `422` menolak request sebelum endpoint berjalan.

```python
Mock(side_effect=httpx.ConnectError("tidak bisa terhubung"))
```

`side_effect` membuat pemanggilan melempar exception. Cara ini mensimulasikan layanan luar yang gagal tanpa menunggu koneksi sungguhan, dan memastikan endpoint menjawab `503` dengan pesan yang benar.

## Menjalankan

Dari folder contoh:

```powershell
pytest -v
```

Hasil sebenarnya:

```text
test_mock.py::test_mock_mengembalikan_nilai_dan_merekam_pemanggilan PASSED
test_mock.py::test_mock_mensimulasikan_kegagalan PASSED
test_mock.py::test_mock_tidak_dipanggil_bila_validasi_gagal PASSED
test_mock.py::test_patch_dibatalkan_setelah_blok_with PASSED
test_monkeypatch.py::test_kurs_tanpa_penggantian_gagal PASSED
test_monkeypatch.py::test_kurs_dengan_fungsi_pengganti PASSED
test_monkeypatch.py::test_salah_tempat_penggantian_tidak_berefek PASSED
test_monkeypatch.py::test_salam_menurut_jam[7-Selamat pagi] PASSED
test_monkeypatch.py::test_salam_menurut_jam[12-Selamat siang] PASSED
test_monkeypatch.py::test_salam_menurut_jam[16-Selamat sore] PASSED
test_monkeypatch.py::test_salam_menurut_jam[21-Selamat malam] PASSED
test_monkeypatch.py::test_mode_bawaan PASSED
test_monkeypatch.py::test_mode_dari_environment PASSED
test_monkeypatch.py::test_perubahan_environment_dibatalkan_otomatis PASSED
============================== 14 passed ==============================
```

Hal yang dibuktikan:

| Pengujian | Yang dibuktikan |
|---|---|
| `test_kurs_tanpa_penggantian_gagal` | Tanpa penggantian, layanan luar dipanggil dan gagal: `503`. |
| `test_kurs_dengan_fungsi_pengganti` | Dengan penggantian, hasil deterministik: `hasil` sama dengan `jumlah × kurs`. |
| `test_salah_tempat_penggantian_tidak_berefek` | Mengganti `layanan.ambil_kurs` tidak berefek karena `main` sudah menyalin namanya. |
| `test_perubahan_environment_dibatalkan_otomatis` | Setelah `test_mode_dari_environment`, `TUGASKU_MODE` kembali ke keadaan semula (`produksi`). |
| `test_patch_dibatalkan_setelah_blok_with` | Setelah blok `with patch.object`, fungsi asli kembali (`503`). |

Pengujian tanpa penggantian selesai dalam sekitar 0,01 detik pada mesin uji karena nama `.invalid` langsung gagal diselesaikan. Pada jaringan lain, waktunya bisa berbeda; itu sebabnya `timeout=2` dipasang pada pemanggilan di `layanan.py`.

### Dokumentasi otomatis

Penggantian tidak memengaruhi `/openapi.json`. Tampilan Swagger UI **belum diverifikasi** lewat browser.

## Kapan memakai yang mana

| Situasi | Alat |
|---|---|
| Hal yang diganti dipasang lewat `Depends` | `app.dependency_overrides` |
| Mengganti satu fungsi atau waktu sementara | `monkeypatch.setattr` |
| Mengganti variabel environment | `monkeypatch.setenv` / `delenv` |
| Perlu memastikan fungsi dipanggil dengan argumen tertentu, atau berapa kali | `Mock` dengan `assert_called_once_with` |
| Mensimulasikan kegagalan layanan luar | `Mock(side_effect=...)` |
| Sesuatu yang berubah terus (waktu, angka acak) | Bungkus dalam fungsi kecil, lalu ganti fungsinya |

Terlalu banyak penggantian membuat pengujian menguji kebohongan: yang diuji hanyalah penggantinya. Ganti hanya yang di luar kendali pengujian (jaringan, waktu, layanan berbayar), dan biarkan logika aplikasi sendiri berjalan asli.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Mengganti nama di modul asal, bukan di modul pemakai | Tidak berefek (teruji: tetap memanggil layanan asli). |
| Memanggil `datetime.now()` langsung di endpoint | Sulit diganti; bungkus dalam fungsi kecil. |
| Membaca environment saat impor modul | Penggantian di pengujian terlambat. Baca saat dipanggil, atau gunakan [Konfigurasi dan Environment](../08-struktur-proyek/konfigurasi-environment.md) dengan override. |
| Mengganti terlalu banyak | Pengujian tidak lagi menguji perilaku nyata. |
| Mengira penggantian bertahan antar pengujian | Dibatalkan otomatis (teruji). Bila perlu di banyak pengujian, taruh di fixture. |
| Lupa `raising=False` saat `delenv` | `KeyError` bila variabel tidak ada (dokumentasi pytest). Tidak diuji. |
| Hanya menguji dengan pengganti yang selalu sukses | Jalur gagal tidak teruji. Pakai `side_effect` untuk kegagalan. |
| Memakai `Mock` tanpa memeriksa pemanggilannya | `Mock` menerima panggilan apa pun tanpa protes; tambahkan `assert_called_once_with` bila pemanggilan itu penting. |

## Latihan

1. **Dasar.** Mengapa `monkeypatch.setattr(layanan, "ambil_kurs", ...)` tidak berpengaruh pada `/kurs`?
2. **Praktik.** Tulis pengujian bahwa `GET /kurs?jumlah=5` menghasilkan `hasil` `50.0` bila kurs diganti menjadi `10.0`.
3. **Prediksi.** Apa isi `GET /mode` setelah `test_mode_dari_environment` selesai, bila dijalankan dalam urutan apa pun?
4. **Analisis.** Kapan `Mock(side_effect=...)` lebih baik dari `lambda` biasa?

??? success "Kunci jawaban"
    Jawaban 1 dan 3 mengacu pada hasil uji di atas. Jawaban 2 adalah penerapan pola yang teruji dan tidak dijalankan. Jawaban 4 adalah penalaran.

    1. Karena `main.py` memakai `from layanan import ambil_kurs`, sehingga nama itu disalin ke modul `main`. Yang dipakai `konversi` adalah `main.ambil_kurs`, jadi penggantian harus di sana.
    2. ```python
       def test_kurs_sepuluh(monkeypatch):
           monkeypatch.setattr(main, "ambil_kurs", lambda: 10.0)
           assert client.get("/kurs", params={"jumlah": 5}).json()["hasil"] == 50.0
       ```
    3. `{"mode": "produksi"}` (nilai asli), karena `monkeypatch` membatalkan perubahan otomatis (`test_perubahan_environment_dibatalkan_otomatis`).
    4. Bila kamu perlu melempar exception (`side_effect`) atau memeriksa berapa kali dan dengan argumen apa fungsi dipanggil (`assert_called_once_with`). `lambda` hanya mengembalikan nilai.

## Ringkasan

- Override dependency untuk yang dipasang lewat `Depends`; `monkeypatch` dan `mock` untuk yang lain.
- `monkeypatch.setattr` mengganti atribut modul, `setenv` dan `delenv` mengatur environment; semua dibatalkan otomatis.
- Ganti nama di modul yang **memakainya**, bukan di modul asalnya.
- `Mock` merekam pemanggilan (`assert_called_once_with`, `assert_not_called`) dan mensimulasikan kegagalan (`side_effect`).
- Bungkus hal yang tak dapat diprediksi (waktu, layanan luar) dalam fungsi kecil agar mudah diganti.
- Ganti seperlunya, supaya pengujian tetap menguji perilaku nyata.

## Langkah berikutnya

Lanjut ke [Proyek Praktik Tahap 5](proyek-tahap-5.md), atau kembali ke daftar materi di [Modul 09: Pengujian](index.md).
