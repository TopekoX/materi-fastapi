# Instalasi dan Virtual Environment

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan fungsi `pip` dan *virtual environment*, serta alasan keduanya dipakai.
- [ ] Membuat dan mengaktifkan virtual environment.
- [ ] Memasang FastAPI di dalamnya.
- [ ] Membuktikan bahwa pemasangan berhasil dan berjalan di environment yang benar.
- [ ] Menyimpan dan memulihkan daftar dependensi proyek dengan `requirements.txt`.

## Prasyarat

- Sudah membaca [Apa itu FastAPI](apa-itu-fastapi.md).
- Python sudah terpasang dan kamu bisa memakai terminal.

## Versi yang dipakai di materi ini

Semua perintah, kode, dan output di Modul 01 dijalankan dengan versi berikut. Halaman lain di materi ini merujuk ke tabel ini.

| Komponen | Versi |
|---|---|
| Python | 3.14.7 |
| pip | 26.2.1 |
| FastAPI | 0.162.0 |
| FastAPI CLI (perintah `fastapi`) | 0.0.32 |
| Pydantic | 2.14.1 |
| Starlette | 1.10.0 |
| Uvicorn | 0.54.0 |
| SQLModel (Modul 06) | 0.0.48 |
| SQLAlchemy (Modul 06, dipasang bersama SQLModel) | 2.1.6 |
| Alembic (Modul 06) | 1.20.1 |
| aiosqlite (Modul 06, sesi async) | 0.22.1 |
| greenlet (Modul 06, sesi async) | 3.5.6 |
| pwdlib dengan argon2-cffi (Modul 07) | 0.3.1 dan 25.1.0 |
| PyJWT (Modul 07) | 2.15.1 |
| python-multipart (Modul 07, ikut terpasang bersama `fastapi[standard]`) | 0.0.32 |
| pydantic-settings (Modul 08) | 2.16.1 |
| python-dotenv (Modul 08, ikut terpasang bersama `fastapi[standard]`) | 1.2.4 |
| pytest (Modul 09) | 9.1.1 |
| httpx (Modul 09, ikut terpasang bersama `fastapi[standard]`) | 0.28.1 |
| pytest-cov dengan coverage (Modul 09) | 7.1.0 dan 7.17.0 |
| anyio (Modul 09, ikut terpasang bersama `fastapi[standard]`) | 4.15.1 |
| asgi-lifespan (Modul 09) | 2.1.0 |
| Sistem operasi | Windows, memakai PowerShell |
| Docker Engine (Modul 10, uji container) | 29.9.2, di Ubuntu Linux |
| Docker Compose (Modul 10) | 5.6.1 |
| Python di dalam image `python:3.14` (Modul 10) | 3.14.9 |
| Nginx, image `nginx:stable-alpine` (Modul 10, reverse proxy) | 1.30.6 |

Berkas `examples/fastapi/requirements.txt` di repositori mengunci FastAPI ke `0.162.0` dan, untuk Modul 06, SQLModel dan Alembic. SQLModel, SQLAlchemy, dan Alembic baru dipakai mulai Modul 06; Modul 01 sampai 05 hanya memerlukan FastAPI.

!!! warning "Yang belum diuji"
    Versi lain, macOS, dan tab macOS/Linux di halaman ini **belum diuji**. Pengujian di Linux (Ubuntu) hanya perintah Docker di Modul 10, serta audit akhir yang menjalankan ulang seluruh rangkaian `pytest` contoh di **Python 3.12.3** dengan versi paket yang sama (hasilnya sama dengan yang tertulis di materi, termasuk satu tes yang memang sengaja gagal di Modul 09; hanya jumlah tes yang dilewati berbeda karena `skipif` bergantung pada platform). Tampilan perintah dan keluaran terminal di halaman tetap berasal dari Windows. Versi minimum Python yang didukung FastAPI juga tidak saya verifikasi; lihat dokumentasi resmi FastAPI. Bila materi dan versi yang kamu pasang berbeda, hasilnya bisa berbeda dari yang tertulis.

## Konsep

### Paket dan `pip`

Python hanya membawa fitur dasar. Fitur tambahan datang dalam bentuk **paket** (*package*), yaitu kode milik orang lain yang bisa kamu pakai. FastAPI adalah salah satu paket. **`pip`** adalah alat untuk memasang paket tersebut.

### Masalah: semua proyek berbagi satu Python

Bayangkan dua proyek. Proyek A butuh versi 1 dari sebuah paket, sedangkan proyek B butuh versi 2. Jika semua paket dipasang ke satu Python yang sama, keduanya saling bentrok.

### Solusi: virtual environment

**Virtual environment** (disingkat *venv*) adalah folder terpisah yang berisi interpreter Python dan paket milik satu proyek saja. Paket yang kamu pasang di dalamnya tidak memengaruhi proyek lain maupun Python bawaan komputermu.

Venv bukan salinan lengkap Python. Pada pengujian, file `pyvenv.cfg` di dalam venv memuat `home = ...` yang menunjuk ke instalasi Python asli, dan `include-system-site-packages = false`, artinya paket milik Python global tidak ikut terbaca.

## Langkah 1: periksa Python

Buka terminal dan jalankan:

```powershell
python --version
```

Output pada pengujian:

```text
Python 3.14.7
```

Jika perintah tidak dikenali, pasang Python lebih dulu. Itu di luar cakupan halaman ini.

## Langkah 2: buat folder proyek dan venv

Buat folder kerja, masuk ke dalamnya, lalu buat venv:

```powershell
python -m venv .venv
```

| Bagian perintah | Artinya |
|---|---|
| `python -m venv` | Menjalankan modul `venv` bawaan Python |
| `.venv` | Nama folder tempat venv dibuat. Nama ini hanya kebiasaan, bebas diganti |

Setelah selesai, folder `.venv` berisi (pada Windows, hasil pengujian): `Include`, `Lib`, `Scripts`, `.gitignore`, dan `pyvenv.cfg`. Struktur di macOS/Linux belum diuji.

!!! tip "Jangan di-commit"
    Folder venv jangan dimasukkan ke Git. Berkas `.gitignore` di dalam `.venv` sudah dibuat otomatis oleh Python, jadi folder itu dilewati oleh Git. Daftar dependensi disimpan terpisah di `requirements.txt` (lihat Langkah 6).

## Langkah 3: aktifkan venv

Mengaktifkan venv membuat perintah `python` dan `pip` di terminal itu menunjuk ke venv, bukan ke Python global.

=== "Windows (PowerShell)"

    ```powershell
    .venv\Scripts\Activate.ps1
    ```

=== "macOS / Linux"

    ```bash
    source .venv/bin/activate
    ```

Cara memastikan venv aktif: variabel `VIRTUAL_ENV` terisi, dan `python` menunjuk ke dalam folder `.venv`. Pada pengujian di PowerShell keduanya terbukti. Biasanya prompt juga diawali `(.venv)`; hal itu tidak dapat diamati pada sesi uji non-interaktif, jadi **belum diverifikasi**. Tab macOS/Linux juga belum diuji.

!!! warning "Aktifkan di setiap terminal baru"
    Aktivasi hanya berlaku untuk terminal yang kamu pakai. Jika membuka terminal baru, jalankan perintah aktivasi lagi.

## Langkah 4: pasang FastAPI

Dengan venv aktif:

```bash
pip install "fastapi[standard]"
```

| Bagian perintah | Artinya |
|---|---|
| `pip install` | Memasang paket |
| `fastapi` | Nama paket |
| `[standard]` | Paket tambahan yang ikut dipasang. Pada pengujian ini ikut terpasang perintah `fastapi` (`fastapi-cli`) dan Uvicorn |
| Tanda kutip `"..."` | Melindungi tanda kurung siku agar tidak ditafsirkan oleh shell tertentu |

Untuk versi yang sama dengan materi ini, pakai versi tertentu:

```bash
pip install "fastapi[standard]==0.162.0"
```

Jika pip menampilkan pemberitahuan bahwa ada versi pip yang lebih baru, itu hanya informasi dan tidak menggagalkan pemasangan.

## Langkah 5: verifikasi pemasangan

Menjalankan perintah tanpa galat belum membuktikan bahwa semuanya berjalan di environment yang benar. Skrip kecil berikut memeriksanya. Simpan sebagai `cek_instalasi.py`:

```python title="cek_instalasi.py"
--8<-- "fastapi/01-pengenalan/instalasi-dan-venv/cek_instalasi.py"
```

### Penjelasan kode

| Baris | Fungsinya |
|---|---|
| `import sys` | Mengambil modul `sys` yang berisi informasi tentang interpreter yang sedang berjalan |
| `from importlib.metadata import version` | Mengambil fungsi `version`, yang membaca versi terpasang sebuah paket |
| `sys.version.split()[0]` | Teks versi Python lengkap, diambil kata pertamanya saja |
| `sys.prefix != sys.base_prefix` | `sys.prefix` adalah lokasi environment yang sedang dipakai, `sys.base_prefix` adalah lokasi Python aslinya. Keduanya berbeda hanya bila kamu berada di dalam venv |
| `version("fastapi")` | Versi paket `fastapi` yang terpasang. Jika paket tidak ada, muncul galat |

### Menjalankan

```bash
python cek_instalasi.py
```

Output di dalam venv (path dipersingkat):

```text
Python         : 3.14.7
Di dalam venv  : True
Lokasi prefix  : C:\...\.venv
FastAPI        : 0.162.0
```

Baris `Di dalam venv : True` dan versi FastAPI yang muncul menandakan pemasangan berhasil di environment yang benar.

### Memeriksa perintah `fastapi`

```bash
fastapi --version
```

Output pada pengujian:

```text
FastAPI CLI version: 0.0.32
FastAPI Cloud CLI version: 0.26.0
```

Angka ini adalah versi alat baris perintah `fastapi`, **bukan** versi paket FastAPI. Untuk versi paketnya, gunakan `cek_instalasi.py` atau `pip list`. Perintah `pip list` menampilkan daftar paket terpasang; pada pengujian, `fastapi 0.162.0`, `pydantic 2.14.1`, `starlette 1.10.0`, dan `uvicorn 0.54.0` ada di dalamnya.

Untuk melihat FastAPI melayani request sungguhan, lanjutkan ke [Endpoint Pertama](endpoint-pertama.md). Halaman itu memuat versi ringkas dari langkah-langkah di halaman ini beserta contoh request dan response.

## Langkah 6: simpan dan pulihkan dependensi

Agar proyekmu dapat dibangun ulang di komputer lain, simpan daftar paket terpasang:

```bash
pip freeze > requirements.txt
```

`pip freeze` mencetak semua paket beserta versi persisnya, dan `> requirements.txt` menuliskannya ke file. Pada pengujian, hasilnya memuat baris seperti `fastapi==0.162.0`, `pydantic==2.14.1`, dan `uvicorn==0.54.0`, bersama paket-paket pendukung lainnya.

Untuk memulihkannya, buat venv baru, aktifkan, lalu:

```bash
pip install -r requirements.txt
```

Pada pengujian, venv baru yang kosong (hanya berisi `pip`) berhasil dipulihkan dengan cara ini, dan `cek_instalasi.py` di dalamnya menampilkan `Di dalam venv : True` serta `FastAPI : 0.162.0`.

## Langkah 7: nonaktifkan venv

Setelah selesai bekerja:

```bash
deactivate
```

Variabel `VIRTUAL_ENV` kembali kosong pada pengujian, dan `python` kembali menunjuk ke Python di luar venv.

## Ringkasan alur untuk proyek baru

1. `python -m venv .venv`
2. Aktifkan venv.
3. `pip install "fastapi[standard]"`
4. `python cek_instalasi.py` untuk memverifikasi.
5. `pip freeze > requirements.txt` untuk menyimpan dependensi.

## Kesalahan umum

Semua kasus berikut dijalankan dan dicatat apa adanya.

### 1. Aktivasi ditolak di PowerShell

Jika kebijakan eksekusi skrip PowerShell adalah `Restricted`, perintah aktivasi gagal:

```text
.\.venv\Scripts\Activate.ps1: File ...\.venv\Scripts\Activate.ps1 cannot be loaded because running scripts is disabled on this system.
```

**Solusi:** izinkan skrip lokal. Perintah berikut mengubah pengaturan PowerShell untuk akun penggunamu saja:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Pada pengujian, aktivasi berhasil ketika PowerShell dijalankan dengan kebijakan `RemoteSigned`. Perintah `Set-ExecutionPolicy` itu sendiri tidak saya jalankan, karena mengubah pengaturan komputer.

### 2. Lupa mengaktifkan venv: paket "tidak ditemukan"

Di luar venv, `python -c "import fastapi"` menghasilkan:

```text
ModuleNotFoundError: No module named 'fastapi'
```

Menjalankan `cek_instalasi.py` di luar venv menampilkan `Di dalam venv : False`, lalu berhenti dengan `PackageNotFoundError: No package metadata was found for fastapi`. **Solusi:** aktifkan venv di terminal itu. Hasil ini hanya berlaku jika FastAPI belum terpasang di Python globalmu.

### 3. Perintah `fastapi` tidak dikenali

Di luar venv, `fastapi --version` di PowerShell menghasilkan pesan bahwa `fastapi` "is not recognized as a name of a cmdlet, function, script file, or executable program". **Solusi:** aktifkan venv tempat FastAPI dipasang.

### 4. Memasang paket ke Python global

Jika `pip install` dijalankan sebelum venv diaktifkan, paket masuk ke Python global dan bukan ke proyekmu. Skenario ini sengaja tidak saya jalankan agar tidak mengubah Python di komputer ini. **Pencegahan:** biasakan memeriksa `VIRTUAL_ENV` atau menjalankan `python cek_instalasi.py` sebelum memasang paket.

## Latihan

1. **Dasar.** Buat venv bernama `.venv-latihan`, aktifkan, lalu pasang FastAPI. Jalankan `python cek_instalasi.py`.
2. **Menengah.** Jalankan `cek_instalasi.py` sekali di dalam venv dan sekali di luarnya (setelah `deactivate`). Bandingkan baris `Di dalam venv` dan jelaskan perbedaannya.
3. **Menengah.** Buat `requirements.txt` dengan `pip freeze`, lalu buat venv kedua dan pulihkan isinya. Buktikan hasilnya dengan `cek_instalasi.py`.
4. **Tantangan.** Pasang versi FastAPI yang berbeda dari milikmu memakai penentu versi (`==`) di venv baru, lalu jelaskan mengapa dua proyek dengan versi berbeda tidak saling mengganggu.

??? success "Petunjuk jawaban"
    1. Hasil yang diharapkan: `Di dalam venv : True` dan versi FastAPI muncul.
    2. Di dalam venv bernilai `True`, di luar venv bernilai `False` (teramati pada pengujian). Perbedaannya: di luar venv, `sys.prefix` dan `sys.base_prefix` sama.
    3. Pada pengujian, langkah ini berhasil dan menghasilkan versi yang sama dengan venv asal.
    4. Latihan ini tidak punya hasil baku karena bergantung pada versi yang kamu pilih, dan versi itu belum saya coba. Alasannya: masing-masing venv menyimpan paketnya sendiri (lihat konsep di atas), sehingga versi di satu venv tidak mengubah venv lain.

## Ringkasan

- `pip` memasang paket Python. Virtual environment memisahkan paket tiap proyek agar tidak bentrok.
- Buat venv dengan `python -m venv .venv`, lalu aktifkan di setiap terminal yang kamu pakai.
- Pasang FastAPI dengan `pip install "fastapi[standard]"`.
- Verifikasi dengan `cek_instalasi.py`, bukan hanya dengan ketiadaan galat.
- `fastapi --version` menampilkan versi alat CLI, bukan versi paket FastAPI.
- Simpan dependensi dengan `pip freeze > requirements.txt`, pulihkan dengan `pip install -r requirements.txt`.
- Jangan memasukkan folder venv ke Git.

## Langkah berikutnya

Lanjutkan ke [Endpoint Pertama](endpoint-pertama.md) untuk membuat dan menjalankan aplikasi FastAPI, atau kembali ke [Modul 01: Pengenalan](index.md).
