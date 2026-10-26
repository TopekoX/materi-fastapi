# Proyek Praktik Tahap 5

## Tujuan pembelajaran

Setelah mengerjakan halaman ini, kamu mampu:

- [ ] Merancang rangkaian pengujian otomatis untuk API yang sudah berjalan.
- [ ] Menyusun `conftest.py` dengan basis data uji, klien, dan fixture pengguna.
- [ ] Menguji autentikasi, otorisasi, validasi, kepemilikan data, error, dan CORS.
- [ ] Mengukur apakah pengujianmu benar-benar menangkap bug dengan merusak aplikasi secara sengaja.
- [ ] Mengukur cakupan kode dengan `pytest-cov` dan memakainya untuk menemukan pengujian yang belum ada.
- [ ] Memakai `-x` dan `--lf` untuk bekerja cepat saat ada pengujian yang gagal.
- [ ] Menguji background task, middleware, dan penanda `skip` dan `xfail` pada contoh dari Modul 08.
- [ ] Menjalankan seluruh rangkaian dengan satu perintah.

## Prasyarat

- Sudah membaca seluruh materi Modul 09: [Pengujian Endpoint](pengujian-endpoint.md), [Fixture](fixture.md), [Override Dependency](override-dependency.md), dan [Basis Data untuk Pengujian](basis-data-pengujian.md).
- Sudah mengerjakan [Proyek: Memecah TugasKu](../08-struktur-proyek/refaktor-tugasku.md). Halaman itu membuktikan perilaku API secara manual dengan 21 request `curl`; halaman ini mengubahnya menjadi pengujian otomatis.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **SQLModel 0.0.48**, **PyJWT 2.15.1**, **pwdlib 0.3.1**, **pydantic-settings 2.16.1**, **pytest 9.1.1**, dan **httpx 0.28.1** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Tentang tahap ini

Tahap 5 melanjutkan **TugasKu API** dari versi modular. **Kode aplikasi tidak berubah**: folder `app/`, `alembic/`, dan `buat_pengelola.py` sama dengan `tahap-4-modular/`. Yang ditambahkan hanya `tests/` dan `pytest.ini`. Kodenya ada di `examples/fastapi/proyek/tahap-5/`.

### Struktur

```text
tahap-5/
├── pytest.ini
├── app/                 (sama dengan tahap-4-modular)
├── alembic/             (sama)
├── buat_pengelola.py    (sama)
└── tests/
    ├── conftest.py
    ├── helpers.py
    ├── test_auth.py
    ├── test_tugas.py
    ├── test_otorisasi.py
    └── test_error_dan_cors.py
```

### Rencana pengujian

Dari kebutuhan API ke berkas pengujian:

| Area | Berkas | Yang diuji |
|---|---|---|
| Pendaftaran dan login | `test_auth.py` | pendaftaran, hash disimpan, nama kembar, validasi, login, pesan yang sama untuk nama tidak ada dan kata sandi salah, token (sembarang, kedaluwarsa, kunci lain, tanpa klaim `sub`, pengguna tidak ada) |
| Tugas | `test_tugas.py` | buat, validasi, judul kembar per pemilik, daftar, filter (selesai, kategori, cari) dan paginasi, ambil satu, ganti (`PUT`), ubah sebagian (`PATCH`, termasuk kategori yang tidak ada), hapus |
| Otorisasi | `test_otorisasi.py` | kategori hanya pengelola, tugas milik orang lain ditolak di semua method, pengelola boleh semuanya, `pemilik_id` tidak bisa ditentukan klien |
| Error dan CORS | `test_error_dan_cors.py` | format error seragam (`404`, `405`), `500` tidak membocorkan rincian, preflight CORS |

## Langkah menjalankan

Dari folder `tahap-5/`:

```powershell
pip install "fastapi[standard]" sqlmodel alembic pyjwt "pwdlib[argon2]" pydantic-settings pytest pytest-cov
pytest
```

Tidak perlu menjalankan `alembic upgrade head`, mengisi `TUGASKU_SECRET_KEY`, atau menjalankan server: pengujian membuat basis data di memori sendiri dan mengisi kunci uji sendiri (lihat `conftest.py`).

## Kode lengkap

### `pytest.ini`

```ini title="pytest.ini"
--8<-- "fastapi/proyek/tahap-5/pytest.ini"
```

`testpaths` memberi tahu pytest untuk mencari pengujian di `tests/`, dan `pythonpath = .` menambahkan folder proyek ke jalur impor sehingga `from app...` berfungsi.

### `tests/conftest.py`

```python title="tests/conftest.py"
--8<-- "fastapi/proyek/tahap-5/tests/conftest.py"
```

### `tests/helpers.py`

```python title="tests/helpers.py"
--8<-- "fastapi/proyek/tahap-5/tests/helpers.py"
```

### `tests/test_auth.py`

```python title="tests/test_auth.py"
--8<-- "fastapi/proyek/tahap-5/tests/test_auth.py"
```

### `tests/test_tugas.py`

```python title="tests/test_tugas.py"
--8<-- "fastapi/proyek/tahap-5/tests/test_tugas.py"
```

### `tests/test_otorisasi.py`

```python title="tests/test_otorisasi.py"
--8<-- "fastapi/proyek/tahap-5/tests/test_otorisasi.py"
```

### `tests/test_error_dan_cors.py`

```python title="tests/test_error_dan_cors.py"
--8<-- "fastapi/proyek/tahap-5/tests/test_error_dan_cors.py"
```

## Penjelasan kode

### Mengisi kunci sebelum mengimpor aplikasi

```python
import os
os.environ.setdefault("TUGASKU_SECRET_KEY", "kunci-khusus-pengujian-yang-cukup-panjang-123456")

from app.main import app
```

Konfigurasi aplikasi dibaca saat `app` diimpor ([Konfigurasi dan Environment](../08-struktur-proyek/konfigurasi-environment.md)), dan kunci wajib terisi. Karena itu kunci uji harus diisi **sebelum** baris `from app...`. `setdefault` tidak menimpa kunci yang sudah ada di environment. Kunci ini hanya untuk pengujian.

### Basis data dan klien

`session` dan `client` mengikuti pola [Basis Data untuk Pengujian](basis-data-pengujian.md): basis data memori baru (dengan `StaticPool`) untuk tiap pengujian, `get_session` diganti lewat `dependency_overrides`, dan override dilepas sesudahnya. Fixture `session` memanggil `engine_uji.dispose()` di akhir untuk menutup koneksi; tanpa itu, jalannya pengujian bersama `pytest-cov` memunculkan peringatan `ResourceWarning: unclosed database` (teramati pada enam peringatan sebelum `dispose()` ditambahkan). `TestClient(app, raise_server_exceptions=False)` membuat `500` dapat diperiksa sebagai response.

### Fixture pengguna dan header

```python
@pytest.fixture
def header_budi(client, session):
    buat_pengguna(session, "budi")
    return header_untuk(client, "budi")
```

- `buat_pengguna` (di `helpers.py`) menaruh pengguna langsung di basis data, termasuk `pengelola` yang tidak bisa dibuat lewat API.
- `header_untuk` benar-benar memanggil `POST /token`, lalu mengembalikan `{"Authorization": "Bearer ..."}`. Jadi alur login ikut teruji setiap kali fixture dipakai.
- Pengujian yang butuh pengguna tinggal meminta `header_budi`, `header_sari`, atau `header_pengelola`, dan `kategori_kuliah` untuk satu kategori awal.

`helpers.py` berisi fungsi biasa (bukan fixture), diimpor dengan `from helpers import ...`. Fixture masuk ke `conftest.py`.

### Pengujian berparameter

`test_validasi_buat_tugas`, `test_parameter_daftar_tidak_valid`, dan `test_patch_menolak_null_untuk_field_wajib` memakai `@pytest.mark.parametrize`: satu fungsi, banyak kasus. Satu kegagalan hanya menandai kasus yang bersangkutan, misalnya `test_validasi_buat_tugas[isian0-body.judul]`.

### Memeriksa efek, bukan hanya status

Beberapa pengujian memeriksa keadaan sesudahnya. `test_tugas_milik_orang_lain_ditolak` memastikan `403` untuk empat method **dan** bahwa data tidak berubah. `test_daftar_menyimpan_hash_bukan_kata_sandi` membaca langsung dari basis data bahwa yang tersimpan adalah hash Argon2.

## Mencoba pengujian

Hasil sebenarnya per berkas dan keseluruhan:

| Berkas | Hasil |
|---|---|
| `test_auth.py` | `15 passed in 0.87s` |
| `test_tugas.py` | `28 passed in 3.51s` |
| `test_otorisasi.py` | `6 passed in 1.06s` |
| `test_error_dan_cors.py` | `5 passed in 0.15s` |

```powershell
pytest
```

```text
......................................................                   [100%]
54 passed in 4.89s
```

Lima puluh empat pengujian selesai dalam sekitar 4,9 detik pada mesin uji, tanpa server berjalan dan tanpa menyentuh basis data sungguhan. Menjalankan berkas dalam urutan terbalik juga memberi `54 passed`, dan satu pengujian bisa dijalankan sendiri (`pytest "tests/test_tugas.py::test_hapus_tugas"` memberi `1 passed`). Itu bukti pengujian tidak bergantung pada urutan atau pada pengujian lain. Waktu bergantung pada mesin, dan pengujian paling lambat adalah yang membuat banyak pengguna, karena hashing Argon2 sengaja lambat.

### Apakah pengujian menangkap bug? Uji dengan merusak aplikasi

"Semua lolos" belum membuktikan pengujiannya bagus; pengujian yang tidak memeriksa apa pun juga lolos. Cara memeriksa mutu pengujian: **rusak aplikasi secara sengaja** (*mutation testing* sederhana) dan lihat apakah pengujian gagal. Dilakukan pada salinan terpisah (folder `tahap-5` tidak diubah), satu kerusakan per percobaan:

| Kerusakan yang disuntikkan | Pengujian yang gagal |
|---|---|
| Hapus pemeriksaan kepemilikan tugas | `test_tugas_milik_orang_lain_ditolak` |
| Daftar tugas tidak disaring per pemilik | `test_daftar_hanya_milik_sendiri` |
| Pendaftaran membuat `pengelola`, bukan `anggota` | `test_daftar_berhasil` |
| Kata sandi disimpan tanpa di-hash | `test_daftar_menyimpan_hash_bukan_kata_sandi` |
| Kategori terbuka untuk semua pengguna login | `test_kategori_hanya_pengelola` |
| Hapus batas minimal panjang judul | `test_validasi_buat_tugas[isian0-body.judul]` |
| Filter `kategori_id` pada daftar diabaikan | `test_filter_kategori` |

Setiap kerusakan menggagalkan tepat satu pengujian (`1 failed, 53 passed`), dan pengujian yang gagal sesuai dengan kerusakannya. Ini bukti bahwa tujuh aturan keamanan, validasi, dan penyaringan tadi benar-benar dijaga rangkaian pengujian. Percobaan ini hanya mencakup tujuh kerusakan; ini bukan jaminan bahwa semua bug tertangkap. (Baris terakhir ditambahkan setelah pengukuran cakupan di bawah menunjukkan filter itu belum diuji.)

### Dokumentasi otomatis

Pengujian tidak memengaruhi `/openapi.json`. Tampilan Swagger UI **belum diverifikasi** lewat browser.

## Mengukur cakupan kode

Uji perusakan hanya mencoba beberapa kerusakan. **Cakupan kode** (*code coverage*) melengkapi dengan cara lain: ia menunjukkan baris mana dari aplikasi yang **tidak pernah dijalankan** oleh pengujian. Alatnya `pytest-cov`:

```powershell
pip install pytest-cov
pytest --cov=app --cov-branch --cov-report=term-missing
```

`--cov=app` mengukur paket `app`, `--cov-branch` ikut memeriksa percabangan (`if`), dan `--cov-report=term-missing` menampilkan nomor baris yang terlewat. Hasil sebenarnya pada rangkaian 54 pengujian:

```text
Name                      Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------------------------
app\config.py                14      0      0      0   100%
app\database.py               9      2      0      0    78%   13-14
app\errors.py                42      0      0      0   100%
app\keamanan.py              38      0      6      0   100%
app\main.py                  12      0      0      0   100%
app\models.py                42      0      0      0   100%
app\routers\auth.py          32      0      6      0   100%
app\routers\kategori.py      16      0      0      0   100%
app\routers\tugas.py         77      0     26      0   100%
---------------------------------------------------------------------
TOTAL                       282      2     38      0    99%
54 passed
```

(Baris `__init__.py` yang kosong tidak ditampilkan.)

**Membacanya:** satu-satunya yang tak terjangkau adalah `app/database.py` baris 13 dan 14, yaitu `get_session` yang asli. Itu wajar: pengujian sengaja menggantinya dengan sesi di memori lewat `dependency_overrides`, jadi versi aslinya tidak dijalankan.

**Cakupan menemukan celah nyata.** Sebelum tiga pengujian ditambahkan, cakupannya `98%` dan melaporkan baris yang terlewat:

| Baris yang terlewat | Artinya | Pengujian yang ditambahkan |
|---|---|---|
| `app/routers/tugas.py:68` | filter `kategori_id` pada `GET /tugas` tidak pernah diuji | `test_filter_kategori` |
| `app/routers/tugas.py:99` | `PATCH` dengan `kategori_id` yang tidak ada tidak diuji | `test_patch_kategori_tidak_ada` |
| `app/keamanan.py:42` | token tanpa klaim `sub` tidak diuji | `test_token_tanpa_klaim_sub_ditolak` |

Hasil tanpa tiga pengujian itu (disimulasikan dengan `-k`): `TOTAL 98%`, dan tiga baris tadi tercantum di kolom `Missing`. Dengan ketiganya, cakupan naik ke `99%`. Cakupan yang naik karena pengujian ditambahkan setelah celahnya terlihat adalah penggunaan yang sehat; cakupan jangan dikejar sebagai angka semata.

!!! warning "Cakupan bukan jaminan"
    Baris yang **dijalankan** belum tentu **diperiksa**. Pengujian yang memanggil endpoint tanpa `assert` yang berarti tetap menaikkan cakupan. Itu sebabnya cakupan dan uji perusakan dipakai bersama: cakupan menunjukkan apa yang belum tersentuh, uji perusakan menunjukkan apakah yang tersentuh benar-benar dijaga. Angka `100%` juga tidak berarti tidak ada bug.

## Bekerja cepat saat ada pengujian gagal

Dua opsi pytest berguna ketika rangkaian sudah besar. Hasil di bawah diperoleh dengan sengaja mengubah satu `assert` di `test_otorisasi.py` agar gagal (lalu dikembalikan):

| Perintah | Hasil sebenarnya |
|---|---|
| `pytest` | `1 failed, 53 passed` |
| `pytest -x` | `1 failed, 20 passed`: berhenti di kegagalan pertama |
| `pytest --lf` (setelah satu kali menjalankan `pytest` dengan cache) | `1 failed`: hanya menjalankan ulang yang terakhir gagal |

`-x` (berhenti pada kegagalan pertama) menghemat waktu saat banyak pengujian rusak sekaligus. `--lf` (*last failed*) menjalankan ulang hanya pengujian yang gagal pada putaran sebelumnya, sehingga perbaikannya cepat dicoba. `--lf` memakai cache pytest (`.pytest_cache`), yang sudah diabaikan oleh `.gitignore` repositori ini.

## Menguji background task, middleware, dan penanda (contoh Modul 08)

Aplikasi TugasKU tidak memakai background task atau middleware buatan sendiri, tetapi contoh di Modul 08 memakainya. Pola pengujiannya ada di `examples/fastapi/09-pengujian/menguji-modul-08/`, yang berisi salinan contoh [Background Task](../08-struktur-proyek/background-task.md) dan [Middleware](../08-struktur-proyek/middleware.md) beserta pengujiannya.

### Background task (`test_background_task.py`, 5 pengujian lolos)

```python title="test_background_task.py"
--8<-- "fastapi/09-pengujian/menguji-modul-08/test_background_task.py"
```

- Fixture `client` memakai `monkeypatch` untuk mengarahkan berkas log ke `tmp_path` dan menghilangkan jeda 2 detik, sehingga pengujian cepat dan tidak mengotori folder.
- Dua tugas latar belakang (dari dependency dan dari endpoint) diperiksa lewat isi log.
- `Mock` memastikan `kirim_notifikasi` dijadwalkan dengan argumen yang benar.
- Validasi yang gagal tidak menjadwalkan tugas, dan tugas yang gagal tidak mengubah status `201`.
- Temuan: **`TestClient` baru kembali setelah tugas latar belakang selesai.** Tanpa mengganti `time.sleep`, satu `POST` memakan lebih dari 2 detik (`lama >= 2.0` lolos). Di server sungguhan klien menerima response lebih dulu; di `TestClient`, pengujian menunggu sampai tugas selesai, sehingga hasil tugas bisa langsung diperiksa.

### Middleware (`test_middleware.py`, 7 pengujian lolos)

```python title="test_middleware.py"
--8<-- "fastapi/09-pengujian/menguji-modul-08/test_middleware.py"
```

Yang diperiksa: header `x-waktu-proses` dan `x-request-id`, `request_id` berbeda tiap request, `request.state` terbaca endpoint, urutan eksekusi lewat `jejak`, `503` pada mode pemeliharaan tanpa menjalankan endpoint, dan perbedaan header pada `HTTPException` dibanding `500`. Fixture `autouse` mengembalikan keadaan awal (`jejak` dan mode pemeliharaan) sebelum dan sesudah tiap pengujian.

### Penanda `skip`, `skipif`, dan `xfail` (`test_penanda.py`)

```python title="test_penanda.py"
--8<-- "fastapi/09-pengujian/menguji-modul-08/test_penanda.py"
```

Hasil dengan `pytest -v -rsx`:

```text
test_penanda.py::test_response_dikompres SKIPPED (fitur kompresi res...)
test_penanda.py::test_khusus_linux SKIPPED (hanya relevan di Linux)
test_penanda.py::test_versi_api_ada_di_response XFAIL (bug yang dike...)
======================== 2 skipped, 1 xfailed ========================
```

- `@pytest.mark.skip(reason=...)`: dilewati tanpa dijalankan.
- `@pytest.mark.skipif(kondisi, reason=...)`: dilewati bila kondisinya benar (di sini bukan Linux, pada mesin uji Windows).
- `@pytest.mark.xfail(reason=..., strict=True)`: diharapkan **gagal** karena bug yang sudah diketahui. Bila ternyata lolos, `strict=True` membuatnya dilaporkan sebagai kegagalan, sehingga kamu tahu bug sudah teratasi dan penandanya harus dihapus. (Perilaku `strict=True` saat tes ternyata lolos tidak diuji di sini.)
- `-rsx` menampilkan alasan untuk `skip` dan `xfail`.

Seluruh folder: `12 passed, 2 skipped, 1 xfailed`.

## Batasan pengujian ini

- **Cakupan 99% bukan jaminan bebas bug.** Cakupan hanya menunjukkan baris yang dijalankan, bukan apakah hasilnya diperiksa. Tujuh kerusakan pada uji perusakan hanya sampel.
- **Pengujian sinkron saja** dengan `TestClient`. Pengujian async dibahas di [Pengujian Async](pengujian-async.md), tetapi tidak diterapkan pada proyek ini.
- **Basis data SQLite di memori.** Perilaku khusus basis data server tidak teruji, dan migrasi Alembic tidak dipakai untuk membuat skema uji, sehingga ketidaksesuaian antara model dan migrasi tidak akan terdeteksi di sini.
- **Tidak ada pengujian beban atau kinerja.**
- **`TestClient` tidak menguji perilaku browser.** Pengujian CORS hanya memeriksa header yang dikirim server; apa yang dilakukan browser terhadapnya tidak teruji. Swagger UI dan tombol *Authorize* juga tidak teruji.
- Alur token hanya diuji sebatas access token. Refresh token dari halaman [Refresh Token dan Pencabutan](../07-autentikasi-keamanan/refresh-token.md) bukan bagian dari proyek ini.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Mengimpor `app` sebelum mengisi `TUGASKU_SECRET_KEY` | Konfigurasi gagal saat impor, dan seluruh pengujian tidak berjalan. |
| Pengujian memakai `database.db` sungguhan | Data uji bercampur dengan data nyata. Selalu ganti `get_session`. |
| Fixture header memakai token yang ditulis tangan | Alur login tidak teruji, dan token bisa kedaluwarsa. Panggil `/token` seperti `header_untuk`. |
| Hanya menguji jalur sukses | Bug otorisasi dan validasi tidak terlihat (lihat percobaan perusakan). |
| Membandingkan seluruh pesan error | Rapuh bila teks berubah. Periksa `kode` dan `field`. |
| Pengujian saling bergantung lewat data | Gagal bila dijalankan sendiri atau dalam urutan lain. Pakai fixture dan basis data baru per pengujian. |
| Mengira 54 lolos berarti tidak ada bug | Hanya berarti kasus yang diuji lolos. |
| Lupa melepas `dependency_overrides` | Bocor ke pengujian lain. Ada di fixture `client`. |

## Latihan

1. **Dasar.** Berkas mana yang kamu buka untuk menambah pengujian "pengguna tidak bisa mendaftar dengan nama berisi spasi"? Apa yang kamu butuhkan dari `conftest.py`?
2. **Praktik.** Tulis pengujian bahwa `PUT /tugas/{id}` dengan `kategori_id` yang tidak ada menghasilkan `404` dengan kode `KATEGORI_TIDAK_ADA`.
3. **Perusakan.** Rusak aplikasi dengan menghapus pemeriksaan `pastikan_judul_unik` di `buat_tugas`. Pengujian mana yang kamu harapkan gagal? Jalankan untuk memeriksa.
4. **Analisis.** Mengapa `header_untuk` memanggil `POST /token`, bukan membuat token langsung dengan `jwt.encode`?

??? success "Kunci jawaban"
    Jawaban 3 mengacu pada percobaan serupa di atas, tetapi kerusakan persisnya tidak dijalankan di halaman ini. Jawaban 1, 2, dan 4 adalah penalaran dan penerapan pola yang teruji; jawaban 1 dan 2 tidak dijalankan.

    1. `tests/test_auth.py`, dengan fixture `client` dari `conftest.py` (dan `@pytest.mark.parametrize` bila ada beberapa kasus). Pendaftaran tidak butuh pengguna terlogin.
    2. ```python
       def test_ganti_tugas_kategori_tidak_ada(client, header_budi):
           dibuat = buat(client, header_budi).json()
           response = client.put(
               f"/tugas/{dibuat['id']}",
               json={"judul": "Judul baru", "kategori_id": 99},
               headers=header_budi,
           )
           assert response.status_code == 404
           assert response.json()["galat"]["kode"] == "KATEGORI_TIDAK_ADA"
       ```
       (`buat` diimpor dari `test_tugas`, seperti di `test_otorisasi.py`.)
    3. `test_judul_kembar_per_pemilik`, karena pengujian itu memastikan judul kembar dijawab `409`. Jalankan `pytest` dan periksa laporannya.
    4. Pemanggilan `/token` ikut menguji alur login dan konfigurasi token yang sebenarnya. Dengan `jwt.encode` langsung, pengujian bisa tetap lolos walau endpoint login rusak.

## Ringkasan

- Tahap 5 menambah rangkaian pengujian otomatis (54 pengujian) pada TugasKU tanpa mengubah kode aplikasi.
- `conftest.py` mengisi kunci uji sebelum impor, menyiapkan basis data memori baru per pengujian, memasang klien, dan menyediakan fixture pengguna dan header.
- Pengujian mencakup autentikasi, validasi, kepemilikan, peran, error seragam, dan CORS.
- Rangkaian tidak bergantung pada urutan, dan bisa dijalankan seluruhnya atau satu per satu.
- Mutu pengujian diuji dengan merusak aplikasi secara sengaja: tujuh kerusakan, masing-masing menggagalkan satu pengujian.
- Cakupan kode (`pytest-cov`) menunjukkan baris yang belum diuji: dari 98% ke 99% setelah tiga pengujian ditambahkan. Cakupan bukan jaminan.
- `-x` dan `--lf` mempercepat bekerja saat ada pengujian gagal; `skip`, `skipif`, dan `xfail` menandai pengujian yang sengaja dilewati atau diharapkan gagal.
- Batasannya: tanpa pengujian sisi browser, dan pengujian async tidak diterapkan pada proyek ini.

## Langkah berikutnya

Kembali ke [Modul 09: Pengujian](index.md). Modul berikutnya adalah [Modul 10: Deployment](../10-deployment/index.md), tempat aplikasi yang sudah teruji ini dikemas dan disiapkan untuk dijalankan.
