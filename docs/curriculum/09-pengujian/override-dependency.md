# Override Dependency

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan mengapa dependency perlu diganti saat pengujian.
- [ ] Memakai `app.dependency_overrides` untuk mengganti konfigurasi, autentikasi, dan layanan luar.
- [ ] Menulis pengganti palsu (*fake*) yang merekam pemanggilan.
- [ ] Melepas semua override setelah tiap pengujian dengan fixture.
- [ ] Mengenali bahaya override yang bocor ke pengujian lain.

## Prasyarat

- Sudah membaca [Fixture](fixture.md).
- Sudah membaca [Konsep Dependency](../05-dependency-injection/konsep-dependency.md), [Dependency Berantai](../05-dependency-injection/dependency-berantai.md), dan [Konfigurasi dan Environment](../08-struktur-proyek/konfigurasi-environment.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **pydantic-settings 2.16.1**, dan **pytest 9.1.1** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Dependency yang menjadi kekuatan aplikasi juga bisa menyulitkan pengujian:

- **Layanan luar** (pengirim email, penyedia pembayaran) lambat, berbayar, atau tidak tersedia saat uji.
- **Autentikasi** membuat setiap pengujian harus login dulu.
- **Konfigurasi** dari environment membuat hasil uji bergantung pada mesin yang menjalankannya.

Menurut dokumentasi FastAPI, kamu bisa mengganti dependency selama pengujian sehingga yang asli (dan sub-dependency-nya) tidak dijalankan. Penggantinya menyediakan nilai yang akan diberikan oleh yang asli. Alatnya adalah `app.dependency_overrides`, sebuah `dict` biasa:

```python
app.dependency_overrides[dependency_asli] = fungsi_pengganti
```

- **Kunci**: fungsi dependency yang **asli** (objeknya, tanpa kurung).
- **Nilai**: fungsi pengganti. FastAPI memanggil pengganti ini sebagai ganti yang asli.

Pengganti membaca parameternya dari request sendiri. Dokumentasi FastAPI mencatat bahwa parameter yang dideklarasikan pengganti-lah yang dibaca FastAPI dari request.

Ini alasan dependency injection dipakai di aplikasi: hal-hal yang ingin diganti saat uji sudah berupa dependency.

## Kode lengkap

Contoh ada di `examples/fastapi/09-pengujian/override-dependency/`.

### `main.py` (aplikasi yang diuji)

```python title="main.py"
--8<-- "fastapi/09-pengujian/override-dependency/main.py"
```

Tiga dependency yang akan diganti: `get_settings` (konfigurasi), `pengguna_saat_ini` (autentikasi sederhana lewat header, bukan keamanan sungguhan), dan `get_pengirim` (layanan luar). `PengirimEmail` sungguhan selalu melempar `RuntimeError`, untuk meniru layanan luar yang tidak bisa dihubungi.

### `conftest.py`

```python title="conftest.py"
--8<-- "fastapi/09-pengujian/override-dependency/conftest.py"
```

### `test_override.py`

```python title="test_override.py"
--8<-- "fastapi/09-pengujian/override-dependency/test_override.py"
```

## Penjelasan kode

### Mengganti konfigurasi

```python
def settings_uji():
    return Settings(nama_aplikasi="TugasKu (uji)", batas_tugas=2)

app.dependency_overrides[get_settings] = settings_uji
```

`get_settings` asli membaca environment dan di-cache. Penggantinya langsung membuat `Settings` dengan nilai yang kita tentukan, tanpa menyentuh environment. Ini cara yang dibahas di dokumentasi FastAPI untuk menguji konfigurasi.

### Mengganti autentikasi

```python
app.dependency_overrides[pengguna_saat_ini] = lambda: "pengguna-uji"
response = client.get("/saya")  # tanpa header
```

Penggantinya (sebuah `lambda` tanpa parameter) tidak membaca header apa pun, sehingga request tanpa `X-Pengguna` tetap sukses. Pengujian yang tidak menguji autentikasi sendiri jadi tidak perlu login.

### Pengganti palsu (fake) yang merekam

```python
class PengirimPalsu(PengirimEmail):
    def __init__(self):
        self.terkirim = []

    def kirim(self, tujuan, isi):
        self.terkirim.append((tujuan, isi))
```

`PengirimPalsu` tidak mengirim apa pun; ia mencatat pemanggilan. Pengujian lalu memeriksa apa yang *akan* dikirim:

```python
assert pengirim.terkirim == [("budi@contoh.id", "Tugas 'Belajar override' dibuat")]
```

Objek yang dibuat sendiri oleh pengujian ini memungkinkan pengujian memeriksa efek samping yang tidak terlihat di response.

### Melepas override

```python
@pytest.fixture(autouse=True)
def bersihkan():
    tugas_db.clear()
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()
    tugas_db.clear()
```

Fixture `autouse` melepas semua override sebelum dan sesudah setiap pengujian. Dokumentasi FastAPI menyebut mengosongkan `app.dependency_overrides` untuk menghapus semua override. Alasan pentingnya ada di bagian jebakan di bawah.

### Beberapa override sekaligus

`test_batas_tugas_tercapai` mengganti tiga dependency dalam satu pengujian (konfigurasi dengan batas 1, pengirim palsu, dan pengguna tetap), lalu memastikan tugas kedua ditolak dengan `409`.

## Menjalankan

Dari folder contoh:

```powershell
pip install pytest pydantic-settings
pytest -v
```

`pydantic-settings` dibutuhkan karena `main.py` memakai `BaseSettings`.

## Mencoba pengujian

Hasil sebenarnya (`pytest -v test_override.py`):

```text
test_override.py::test_info_memakai_konfigurasi_bawaan PASSED
test_override.py::test_info_dengan_konfigurasi_pengganti PASSED
test_override.py::test_tanpa_override_butuh_header PASSED
test_override.py::test_autentikasi_diganti_pengguna_tetap PASSED
test_override.py::test_buat_tugas_tanpa_override_gagal_karena_email PASSED
test_override.py::test_buat_tugas_dengan_pengirim_palsu PASSED
test_override.py::test_batas_tugas_tercapai PASSED
test_override.py::test_override_sudah_dilepas PASSED
============================== 8 passed ==============================
```

Beberapa hal yang dibuktikan:

| Pengujian | Yang dibuktikan |
|---|---|
| `test_info_memakai_konfigurasi_bawaan` | Tanpa override, `/info` mengembalikan `{"nama_aplikasi": "TugasKu", "batas_tugas": 100}`. |
| `test_info_dengan_konfigurasi_pengganti` | Dengan override, `/info` mengembalikan nilai pengganti. |
| `test_tanpa_override_butuh_header` | Tanpa override, `/saya` tanpa header `422`, dengan pengguna `hantu` `401`. |
| `test_autentikasi_diganti_pengguna_tetap` | Dengan override, `/saya` tanpa header `200` dan `{"pengguna": "pengguna-uji"}`. |
| `test_buat_tugas_tanpa_override_gagal_karena_email` | Tanpa mengganti pengirim, `POST /tugas` menghasilkan `500` (`RuntimeError` dari pengirim asli). |
| `test_buat_tugas_dengan_pengirim_palsu` | Dengan pengirim palsu, `201` dan isi email yang akan dikirim terekam. |
| `test_batas_tugas_tercapai` | Tugas pertama `201`, kedua `409` dengan `{"detail": "Batas jumlah tugas tercapai"}`. |

Pengujian `500` memakai `TestClient(app, raise_server_exceptions=False)` di `conftest.py`. Bawaannya, `TestClient` melempar kembali exception server ke dalam pengujian; pengaturan ini membuatnya mengembalikan response `500` biasa agar bisa di-`assert`.

### Jebakan: override yang bocor

`test_override_bocor.py` memasang override tanpa melepasnya:

```python title="test_override_bocor.py"
--8<-- "fastapi/09-pengujian/override-dependency/test_override_bocor.py"
```

Karena `conftest.py` memiliki fixture pembersih `autouse`, pengujian ini lolos di folder tersebut (hasil: `2 passed`). Untuk melihat masalahnya, abaikan `conftest.py` dengan `--noconftest`:

```powershell
pytest test_override_bocor.py --noconftest
```

```text
test_override_bocor.py::test_ubah_konfigurasi_tanpa_melepas PASSED
test_override_bocor.py::test_mengira_konfigurasi_asli FAILED
E       AssertionError: assert 'PALSU' == 'TugasKu'
========================= 1 failed, 1 passed =========================
```

`test_mengira_konfigurasi_asli` gagal, padahal kodenya benar: override dari pengujian sebelumnya masih terpasang di `app`. Karena `app` adalah objek yang dipakai bersama, override adalah **keadaan global**. Selalu lepas override, paling aman lewat fixture `autouse` seperti `bersihkan`.

### Seluruh pengujian

`pytest` pada folder penuh: `10 passed` (delapan di `test_override.py`, dua di `test_override_bocor.py` karena dibersihkan oleh `conftest.py`).

### Konfigurasi asli dari environment

Tanpa override, `get_settings()` membaca environment. Dengan `TUGASKU_BATAS_TUGAS=7`, `get_settings().batas_tugas` bernilai `7` (teruji). Pengujian yang bergantung pada environment mesin seperti ini rapuh, sehingga override lebih disukai.

### Dokumentasi otomatis

Override tidak memengaruhi `/openapi.json`. Tampilan Swagger UI **belum diverifikasi** lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Lupa melepas override | Bocor ke pengujian lain (teruji: `PALSU` terbaca di pengujian berikutnya). |
| Memakai fungsi yang salah sebagai kunci (misalnya `get_settings()` dengan kurung) | Kunci harus fungsi aslinya (objek), bukan hasil panggilannya. Tidak diuji. |
| Pengganti tidak menerima parameter yang dibutuhkan | Parameter pengganti-lah yang dibaca FastAPI; deklarasikan sesuai kebutuhan (dokumentasi FastAPI). |
| Mengganti terlalu banyak | Pengujian tidak lagi menguji perilaku nyata. Ganti hanya yang perlu (layanan luar, waktu, konfigurasi). |
| Mengira override menguji dependency aslinya | Dependency asli tidak dijalankan. Uji dependency asli secara terpisah (contoh: `test_tanpa_override_butuh_header`). |
| Memakai `raise_server_exceptions=True` (bawaan) lalu mengharapkan `500` | Exception dilempar ke pengujian. Gunakan `raise_server_exceptions=False` untuk memeriksa response `500`. |
| Mengganti dependency dengan versi yang selalu sukses tanpa menguji kasus gagalnya | Jalur gagal tidak teruji. Buat juga pengganti yang gagal. |
| Override di tingkat modul tanpa pembersih | Berlaku selama seluruh sesi pengujian. |

## Latihan

1. **Dasar.** Apa kunci dan nilai pada `app.dependency_overrides[get_settings] = settings_uji`?
2. **Prediksi.** Apa status `POST /tugas` bila hanya pengirim yang diganti, tanpa header `X-Pengguna`? Mengapa?
3. **Praktik.** Tulis pengujian yang memastikan `PengirimPalsu` merekam **dua** email setelah dua tugas dibuat.
4. **Analisis.** Mengapa `test_override_bocor.py` lolos di folder contoh, tetapi gagal dengan `--noconftest`?

??? success "Kunci jawaban"
    Jawaban 4 mengacu pada hasil uji di atas. Jawaban 1 sampai 3 adalah penalaran dan penerapan pola yang teruji; jawaban 2 dan 3 tidak dijalankan.

    1. Kunci: fungsi `get_settings` yang asli. Nilai: `settings_uji`, fungsi pengganti yang dipanggil FastAPI sebagai ganti yang asli.
    2. `422`: dependency `pengguna_saat_ini` yang asli tetap berjalan dan membutuhkan header `X-Pengguna` (pola yang sama dengan `test_tanpa_override_butuh_header`, yang menghasilkan `422`).
    3. ```python
       def test_dua_email_terekam(client):
           pengirim = PengirimPalsu()
           app.dependency_overrides[get_pengirim] = lambda: pengirim
           app.dependency_overrides[pengguna_saat_ini] = lambda: "budi"
           client.post("/tugas", json={"judul": "Tugas satu"})
           client.post("/tugas", json={"judul": "Tugas dua"})
           assert len(pengirim.terkirim) == 2
       ```
    4. Di folder contoh, `conftest.py` menjalankan fixture `autouse` `bersihkan` yang melepas override sebelum setiap pengujian. Dengan `--noconftest`, fixture itu tidak ada, sehingga override dari pengujian pertama masih terpasang saat pengujian kedua berjalan.

## Ringkasan

- `app.dependency_overrides` mengganti dependency selama pengujian: kunci fungsi aslinya, nilai fungsi penggantinya.
- Gunakan untuk mengganti konfigurasi, autentikasi, dan layanan luar yang lambat, berbayar, atau tidak tersedia.
- Pengganti palsu (*fake*) bisa merekam pemanggilan agar efek samping dapat diperiksa.
- Override adalah keadaan global pada `app`: lepas setelah tiap pengujian dengan fixture `autouse`.
- Jangan mengganti lebih dari yang perlu, dan uji juga dependency aslinya.
- `TestClient(app, raise_server_exceptions=False)` membuat `500` bisa diperiksa sebagai response.

## Langkah berikutnya

Lanjut ke [Basis Data untuk Pengujian](basis-data-pengujian.md), atau kembali ke daftar materi di [Modul 09: Pengujian](index.md).
