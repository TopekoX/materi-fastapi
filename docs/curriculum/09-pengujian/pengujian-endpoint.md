# Pengujian Endpoint

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan mengapa API perlu pengujian otomatis.
- [ ] Menulis pengujian endpoint dengan `TestClient` dan `pytest`.
- [ ] Menguji status, isi JSON, header, parameter query, dan body.
- [ ] Menguji kasus sukses, kasus gagal (`404`, `401`, `422`), dan validasi.
- [ ] Menjalankan `pytest`, memilih pengujian dengan `-k`, dan membaca laporan kegagalan.
- [ ] Mengenali pengujian yang saling bergantung lewat data bersama.

## Prasyarat

- Sudah membaca [Proyek: Memecah TugasKu](../08-struktur-proyek/refaktor-tugasku.md). Halaman itu membuktikan perilaku API secara manual dengan `curl`; halaman ini mengubah cara itu menjadi pengujian otomatis.
- Sudah membaca [Status Code](../04-penanganan-error/status-code.md) dan [Error Validasi](../04-penanganan-error/error-validasi.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **pytest 9.1.1**, dan **httpx 0.28.1** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

### Mengapa menguji otomatis

Di modul-modul sebelumnya kita membuktikan API dengan menjalankan server dan mengirim request lewat `curl`. Itu cukup untuk belajar, tetapi:

- harus dilakukan ulang secara manual setiap kali kode berubah,
- mudah ada yang terlewat,
- tidak ada catatan yang menyatakan "ini seharusnya begini".

**Pengujian otomatis** adalah kode yang menjalankan API dan memeriksa hasilnya. Sekali ditulis, bisa dijalankan kapan saja dalam hitungan detik, dan memberi tahu bila perubahan merusak perilaku yang sudah benar.

### `TestClient` dan `pytest`

Dua alat yang dipakai:

| Alat | Fungsi |
|---|---|
| **`TestClient`** | Bawaan FastAPI (dibangun di atas `httpx`). Mengirim request ke aplikasi **tanpa menjalankan server**. |
| **`pytest`** | Kerangka pengujian: menemukan fungsi bernama `test_...`, menjalankannya, dan melaporkan hasil. |

Menurut dokumentasi FastAPI, tes ditulis sebagai fungsi `def` biasa (bukan `async def`), memakai `assert` biasa, dan `TestClient` dipanggil tanpa `await`. Aturan pytest sederhana: berkas bernama `test_*.py`, fungsi bernama `test_*`, dan pengujian **gagal** bila ada `assert` yang bernilai salah atau terjadi exception.

### Pemasangan

```powershell
pip install pytest
```

`httpx` yang dibutuhkan `TestClient` sudah ikut terpasang bersama `fastapi[standard]` (teruji: terpasang di venv uji).

## Kode lengkap

Contoh ada di `examples/fastapi/09-pengujian/pengujian-endpoint/`.

### `main.py` (aplikasi yang diuji)

```python title="main.py"
--8<-- "fastapi/09-pengujian/pengujian-endpoint/main.py"
```

Aplikasi kecil dengan data di memori dan satu endpoint yang butuh header `X-Token`. Token contoh itu bukan cara autentikasi yang aman; dipakai hanya untuk memperlihatkan pengujian header.

### `test_main.py` (pengujian)

```python title="test_main.py"
--8<-- "fastapi/09-pengujian/pengujian-endpoint/test_main.py"
```

## Penjelasan kode

### Membuat klien

```python
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
```

`TestClient(app)` membungkus aplikasi. `client.get(...)`, `client.post(...)`, dan sebagainya mengirim request langsung ke aplikasi dan mengembalikan objek response, tanpa `fastapi dev` dan tanpa port.

### Pola satu pengujian: siapkan, jalankan, periksa

```python
def test_buat_tugas():
    tugas_db.clear()
    response = client.post("/tugas", json={"judul": "Belajar pytest"})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "judul": "Belajar pytest", "selesai": False}
```

1. **Siapkan** keadaan awal (`tugas_db.clear()`).
2. **Jalankan** aksi yang diuji (`client.post(...)`).
3. **Periksa** hasilnya dengan `assert`.

### Cara mengirim data

| Kebutuhan | Cara |
|---|---|
| Parameter query | `client.get("/tugas", params={"selesai": True})` |
| Body JSON | `client.post("/tugas", json={...})` |
| Header | `client.delete("/tugas/1", headers={"X-Token": "..."})` |
| Data formulir | `data={...}` (menurut dokumentasi FastAPI) |
| Cookie | `cookies={...}` (menurut dokumentasi FastAPI) |

Baris `data=` dan `cookies=` tidak dipakai di contoh ini.

### Memeriksa hasil

- `response.status_code` untuk status.
- `response.json()` untuk isi JSON (dibandingkan dengan `dict` atau `list` yang diharapkan).
- Untuk error validasi, periksa bagian yang penting saja (`type` dan `loc`), bukan seluruh pesan, supaya tes tidak rapuh bila teks pesan berubah:

```python
galat = response.json()["detail"][0]
assert galat["type"] == "string_too_short"
assert galat["loc"] == ["body", "judul"]
```

### Menguji kasus gagal

Pengujian yang baik mencakup bukan hanya jalur sukses. `test_ambil_tugas_tidak_ada` memastikan `404`, `test_buat_tugas_judul_terlalu_pendek` memastikan `422`, dan `test_hapus_butuh_token` memeriksa tiga keadaan: tanpa header (`422`), token salah (`401`), dan token benar (`204`).

## Menjalankan

Dari folder contoh:

```powershell
pytest
```

atau `python -m pytest`, yang juga menambahkan folder saat ini ke jalur impor sehingga `from main import app` berfungsi. Berikut hasil sebenarnya dengan `pytest -v test_main.py`:

```text
collected 6 items

test_main.py::test_beranda PASSED                                        [ 16%]
test_main.py::test_buat_tugas PASSED                                     [ 33%]
test_main.py::test_buat_tugas_judul_terlalu_pendek PASSED                [ 50%]
test_main.py::test_ambil_tugas_tidak_ada PASSED                          [ 66%]
test_main.py::test_filter_selesai PASSED                                 [ 83%]
test_main.py::test_hapus_butuh_token PASSED                              [100%]

============================== 6 passed ==============================
```

Tanpa `-v`, hasilnya ringkas: satu titik per pengujian yang lolos.

```text
test_main.py ......                                                      [100%]

============================== 6 passed in 0.30s ==============================
```

Waktu `0,30s` bergantung pada mesin. Seluruh enam pengujian selesai dalam waktu singkat, tanpa server berjalan.

### Memilih pengujian

`-k` memilih pengujian berdasarkan nama:

```powershell
pytest test_main.py -k "hapus" -v
```

```text
collected 6 items / 5 deselected / 1 selected
test_main.py::test_hapus_butuh_token PASSED
======================= 1 passed, 5 deselected =======================
```

Cara lain: `pytest test_main.py::test_beranda` untuk satu fungsi tertentu.

### Membaca kegagalan

Bila `assert` salah, pytest menjelaskan perbedaannya. Contoh (hasil sebenarnya) saat nilai `selesai` yang diharapkan sengaja dibuat `True`, padahal aplikasi mengembalikan `False`:

```text
>       assert response.json() == {"id": 1, "judul": "Belajar pytest", "selesai": True}
E       AssertionError: assert {'judul': 'Be...alse, 'id': 1} == {'id': 1, 'ju...elesai': True}
E         Differing items:
E         {'selesai': False} != {'selesai': True}
FAILED test_gagal.py::test_buat_tugas - AssertionError: ...
```

Tanda `>` menunjuk baris yang gagal, dan baris `E` menunjukkan item yang berbeda. Membaca laporan ini adalah keterampilan utama dalam pengujian.

## Jebakan: pengujian yang saling bergantung

Perhatikan bahwa hampir setiap tes di atas memanggil `tugas_db.clear()` di awal. Alasannya ada di `test_masalah_state.py`:

```python title="test_masalah_state.py"
--8<-- "fastapi/09-pengujian/pengujian-endpoint/test_masalah_state.py"
```

Dua pengujian ini berbagi `tugas_db` (data di memori yang sama). Hasil sebenarnya bila dijalankan bersama:

```text
>       assert response.json() == []
E       AssertionError: assert [{'judul': 'T...lse, 'id': 1}] == []
E         Left contains one more item: {'judul': 'Tugas dari tes A', 'selesai': False, 'id': 1}
FAILED test_masalah_state.py::test_b_mengira_daftar_kosong
========================= 1 failed, 1 passed =========================
```

Namun `test_b_mengira_daftar_kosong` **lolos** bila dijalankan sendirian:

```powershell
pytest "test_masalah_state.py::test_b_mengira_daftar_kosong"
```

```text
============================== 1 passed ==============================
```

Hasil sebuah pengujian bergantung pada pengujian lain yang berjalan sebelumnya. Ini kesalahan klasik: pengujian yang baik **tidak boleh bergantung pada urutan atau pada sisa data pengujian lain**. `tugas_db.clear()` di setiap tes memang menambal masalah, tetapi mudah terlupa. Cara yang lebih rapi, *fixture*, dibahas di halaman berikutnya.

### Dokumentasi otomatis

Pengujian tidak memengaruhi `/openapi.json`. Tampilan Swagger UI **belum diverifikasi** lewat browser.

## Apa yang tidak dijangkau `TestClient`

`TestClient` menguji aplikasi tanpa server dan tanpa browser. Karena itu ia **tidak** menguji perilaku sisi browser seperti CORS yang ditegakkan browser atau tampilan Swagger UI. Ia juga tidak menguji pengaturan penyebaran (server, HTTPS, proses). Header CORS yang dikirim server bisa diperiksa dengan `TestClient`, tetapi apa yang dilakukan browser terhadapnya tidak.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Nama berkas atau fungsi tidak berawalan `test_` | pytest tidak menemukannya dan tidak menjalankannya. Tidak diuji di sini. |
| Menulis tes dengan `async def` untuk `TestClient` | Tidak perlu; dokumentasi FastAPI menganjurkan `def` biasa. |
| Tes saling bergantung lewat data bersama | Lolos atau gagal tergantung urutan (teruji). |
| Membandingkan seluruh pesan error | Tes rapuh bila teks berubah. Periksa `type` dan `loc`. |
| Hanya menguji jalur sukses | Kegagalan tidak terdeteksi. Uji juga `404`, `401`, `422`. |
| Mengirim model Pydantic ke `json=` | `TestClient` butuh data yang bisa dijadikan JSON (dokumentasi FastAPI). Ubah dulu dengan `jsonable_encoder`. Tidak diuji. |
| Menjalankan `pytest` dari folder yang salah | Impor `from main import app` gagal. Jalankan dari folder yang berisi `main.py`, atau dengan `python -m pytest`. Tidak diuji di sini. |
| Mengira "semua tes lolos" berarti tidak ada bug | Hanya berarti kasus yang diuji lolos. |

## Latihan

1. **Dasar.** Tulis pengujian yang memastikan `GET /tugas/1` menghasilkan `200` setelah `POST /tugas` berhasil membuat tugas pertama.
2. **Kasus gagal.** Tulis pengujian untuk `POST /tugas` dengan `"judul": 123` (angka). Status dan `type` apa yang kamu harapkan?
3. **Prediksi.** Pada `test_masalah_state.py`, apa yang terjadi bila urutan kedua fungsi dibalik?
4. **Analisis.** Mengapa `test_hapus_butuh_token` memeriksa tiga keadaan dalam satu fungsi, dan apa kekurangannya?

??? success "Kunci jawaban"
    Jawaban 1 sampai 3 dijalankan dengan pytest. Jawaban 4 adalah penalaran.

    1. ```python
       def test_ambil_tugas_setelah_dibuat():
           tugas_db.clear()
           client.post("/tugas", json={"judul": "Tugas pertama"})
           response = client.get("/tugas/1")
           assert response.status_code == 200
           assert response.json()["judul"] == "Tugas pertama"
       ```
    2. Status `422`, `type` `string_type`, dan `loc` `["body", "judul"]` (hasil uji). Pydantic menolak angka untuk field `str`.
    3. Dengan urutan dibalik (`test_b` lebih dulu, `test_a` sesudahnya), kedua pengujian **lolos** (hasil uji: `2 passed`), karena daftar masih kosong saat `test_b` berjalan. Tetapi `test_a` meninggalkan satu tugas di `tugas_db`, jadi pengujian berikutnya (misalnya `test_b` dari `test_masalah_state.py` yang dijalankan sesudahnya) gagal. Hasil uji pada urutan itu: `1 failed, 3 passed`. Kesimpulannya: lolos atau gagalnya sebuah tes bergantung pada urutan dan sisa data, bukan pada kebenaran kodenya.
    4. Satu fungsi memeriksa tiga skenario berurutan yang saling bergantung (tugas harus sudah ada, token benar menghapusnya). Kekurangannya: bila yang pertama gagal, yang lain tidak dijalankan dan sulit tahu skenario mana yang rusak. Memecah menjadi tiga tes yang masing-masing menyiapkan datanya sendiri lebih jelas.

## Ringkasan

- Pengujian otomatis menjalankan API dan memeriksa hasilnya, tanpa server dan tanpa manual.
- `TestClient(app)` mengirim request ke aplikasi; `pytest` menemukan fungsi `test_*`, menjalankannya, dan melaporkan hasil.
- Pola satu pengujian: siapkan, jalankan, periksa dengan `assert`.
- Data dikirim lewat `params=`, `json=`, dan `headers=`.
- Uji jalur sukses dan jalur gagal; periksa `type` dan `loc` untuk error validasi.
- Pengujian tidak boleh bergantung pada urutan atau sisa data pengujian lain.
- `TestClient` tidak menguji perilaku browser atau penyebaran.

## Langkah berikutnya

Lanjut ke [Fixture](fixture.md), atau kembali ke daftar materi di [Modul 09: Pengujian](index.md).
