# Konfigurasi dan Environment

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan mengapa konfigurasi dipisah dari kode.
- [ ] Mendefinisikan konfigurasi dengan `BaseSettings` dari `pydantic-settings`.
- [ ] Mengisi konfigurasi lewat variabel environment dan berkas `.env`.
- [ ] Menjelaskan urutan prioritas: environment mengalahkan `.env`, yang mengalahkan nilai bawaan.
- [ ] Menyembunyikan rahasia dengan `SecretStr` dan tidak mengembalikannya di response.
- [ ] Memakai `lru_cache` agar konfigurasi dibaca sekali.

## Prasyarat

- Sudah membaca [Router Modular](router-modular.md).
- Sudah membaca [Token](../07-autentikasi-keamanan/token.md), terutama bagian kunci penandatangan dari environment.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **Pydantic 2.14.1**, **pydantic-settings 2.16.1**, dan **python-dotenv 1.2.4** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

### Masalah: nilai yang tertanam di kode

Di modul-modul sebelumnya, beberapa nilai ditulis langsung di kode: alamat basis data (`sqlite:///database.db`), masa berlaku token, dan daftar origin CORS. Itu menimbulkan masalah:

- Nilai berbeda di setiap lingkungan (laptopmu, server pengujian, server produksi), tetapi kodenya sama.
- Rahasia (kunci penandatangan token, kata sandi basis data) ikut masuk ke Git bila ditulis di kode.
- Mengubah satu nilai berarti mengubah dan menyebarkan kode lagi.

Praktik umumnya: kode **membaca** konfigurasi dari luar, dan nilai sebenarnya disediakan oleh lingkungan tempat aplikasi berjalan.

### Variabel environment dan `.env`

**Variabel environment** adalah pasangan nama dan nilai yang disediakan sistem operasi untuk proses yang berjalan. Di PowerShell:

```powershell
$env:TUGASKU_NAMA_APLIKASI = "Aplikasi Saya"
```

Variabel ini hanya berlaku untuk sesi terminal itu. Untuk kenyamanan saat pengembangan, nilai-nilai boleh ditaruh dalam berkas **`.env`** yang dibaca aplikasi. Karena `.env` biasanya berisi rahasia, **jangan di-commit**; commit berkas contoh (di sini `.env.contoh`) yang tidak berisi rahasia asli.

### `pydantic-settings`

Pustaka `pydantic-settings` membaca konfigurasi ke dalam kelas Pydantic. Keuntungannya: nilai (yang selalu berupa teks di environment) otomatis **dikonversi dan divalidasi** memakai tipe dan `Field`, persis seperti model yang kamu kenal dari Modul 03. Dokumentasi FastAPI memakai pustaka ini untuk pengaturan aplikasi.

### Pemasangan

```powershell
pip install pydantic-settings python-dotenv
```

Dokumentasi FastAPI menyebut `python-dotenv` dibutuhkan untuk membaca berkas `.env`; pada venv uji, `python-dotenv` sudah terpasang bersama `fastapi[standard]`.

## Kode lengkap

Contoh ada di `examples/fastapi/08-struktur-proyek/konfigurasi-environment/`.

### `config.py`

```python title="config.py"
--8<-- "fastapi/08-struktur-proyek/konfigurasi-environment/config.py"
```

### `main.py`

```python title="main.py"
--8<-- "fastapi/08-struktur-proyek/konfigurasi-environment/main.py"
```

### `.env.contoh`

```text title=".env.contoh"
--8<-- "fastapi/08-struktur-proyek/konfigurasi-environment/.env.contoh"
```

## Penjelasan kode

### Kelas `Settings`

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TUGASKU_", env_file=".env")

    nama_aplikasi: str = "TugasKu"
    mode_debug: bool = False
    database_url: str = "sqlite:///database.db"
    detik_akses: int = Field(default=900, ge=60)
    origin_diizinkan: list[str] = ["http://localhost:3000"]
    secret_key: SecretStr = Field(min_length=32)
```

- `env_prefix="TUGASKU_"`: hanya variabel berawalan `TUGASKU_` yang dibaca, sehingga tidak bentrok dengan variabel lain di sistem. Variabel `TUGASKU_DETIK_AKSES` mengisi field `detik_akses`.
- `env_file=".env"`: membaca berkas `.env` di folder kerja bila ada.
- Nama variabel dicocokkan **tanpa membedakan huruf besar-kecil** (dokumentasi FastAPI). Pada pengujian, `tugasku_mode_debug=true` (huruf kecil) tetap mengisi `mode_debug`.
- Field yang punya nilai bawaan bersifat opsional. `secret_key` **tidak punya** nilai bawaan, jadi wajib diisi.
- `detik_akses` memakai `ge=60`: konfigurasi divalidasi dengan aturan `Field` seperti model biasa.
- `secret_key: SecretStr` adalah teks yang disembunyikan saat dicetak. Nilai aslinya dibaca dengan `.get_secret_value()`.

### `get_settings` dan `lru_cache`

```python
@lru_cache
def get_settings() -> Settings:
    return Settings()
```

Membuat `Settings()` membaca environment dan berkas `.env`. `@lru_cache` membuat fungsi hanya dijalankan **sekali**; panggilan berikutnya mengembalikan objek yang sama. Menurut dokumentasi FastAPI, karena fungsi tanpa argumen ini berperan seperti variabel global tetapi tetap bisa diganti (di pengujian), ia dibungkus sebagai dependency: `Annotated[Settings, Depends(get_settings)]`.

### Dipakai di dua tempat

- **Saat aplikasi disusun** (`settings = get_settings()` di tingkat modul): judul aplikasi, mode debug, dan daftar origin CORS ditentukan dari konfigurasi.
- **Di endpoint** lewat `SettingsDep`.

### Jangan membocorkan rahasia

Endpoint `/info` hanya mengembalikan nilai yang aman, ditambah `panjang_secret_key` sebagai bukti kunci terbaca tanpa menampilkannya. `secret_key` itu sendiri tidak pernah dikembalikan.

## Menjalankan

Buat kunci acak dan jalankan:

```powershell
$env:TUGASKU_SECRET_KEY = (python -c "import secrets; print(secrets.token_hex(32))")
fastapi dev main.py
```

Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah. Atau salin `.env.contoh` menjadi `.env` dan isi nilainya (`.env` sudah masuk `.gitignore` repositori ini).

## Mencoba request

Hasil di bawah dijalankan dengan `curl.exe`.

### Hanya dari environment

```powershell
curl.exe http://127.0.0.1:8000/info
```

```json
{"nama_aplikasi":"TugasKu","mode_debug":false,"database_url":"sqlite:///database.db","detik_akses":900,"origin_diizinkan":["http://localhost:3000"],"panjang_secret_key":64}
```

Hanya `TUGASKU_SECRET_KEY` yang diisi; sisanya memakai nilai bawaan. CORS dari konfigurasi: request dengan `Origin: http://localhost:3000` mendapat header `access-control-allow-origin: http://localhost:3000`, sedangkan `Origin: http://lain.example.com` tidak mendapat header itu.

### Dari berkas `.env`

Dengan `.env` berisi `TUGASKU_SECRET_KEY` (64 karakter), `TUGASKU_NAMA_APLIKASI=TugasKu dari .env`, dan `TUGASKU_DETIK_AKSES=1800`:

```json
{"nama_aplikasi":"TugasKu dari .env","mode_debug":false,"database_url":"sqlite:///database.db","detik_akses":1800,"origin_diizinkan":["http://localhost:3000"],"panjang_secret_key":64}
```

### Prioritas

Dengan `.env` yang sama, menjalankan server dengan `TUGASKU_DETIK_AKSES=120` di environment:

```text
detik_akses: 120
nama_aplikasi: TugasKu dari .env
```

`detik_akses` mengikuti environment (120), sedangkan `nama_aplikasi` tetap dari `.env`. Urutan prioritas yang teramati: **environment**, lalu **`.env`**, lalu **nilai bawaan**.

### Validasi saat mulai

Konfigurasi yang salah menggagalkan aplikasi **sejak mulai**, bukan saat request pertama. Hasil membuat `Settings()` pada berbagai kondisi:

| Kondisi | Hasil |
|---|---|
| `TUGASKU_SECRET_KEY` tidak diisi | `ValidationError`: `secret_key  Field required [type=missing, ...]` |
| `TUGASKU_SECRET_KEY=pendek` | `Value should have at least 32 items after validation, not 6 [type=too_short, ...]` |
| `TUGASKU_DETIK_AKSES=banyak` | `Input should be a valid integer, unable to parse string as an integer [type=int_parsing, ...]` |
| `TUGASKU_DETIK_AKSES=10` | `Input should be greater than or equal to 60 [type=greater_than_equal, ...]` |

Menjalankan `fastapi dev main.py` dengan `TUGASKU_DETIK_AKSES=banyak` juga berakhir dengan `ValidationError` untuk `detik_akses`; server tidak mulai.

### Konversi tipe

Dengan `tugasku_mode_debug=true`, `TUGASKU_DETIK_AKSES=300`, dan `TUGASKU_ORIGIN_DIIZINKAN='["https://a.example.com","https://b.example.com"]'`, hasilnya `True`, `300`, dan list dua origin. Environment hanya berisi teks; `pydantic-settings` mengubahnya menjadi `bool`, `int`, dan `list` (daftar ditulis sebagai teks JSON).

### Rahasia di `print`

```text
**********
Settings(nama_aplikasi='TugasKu', mode_debug=False, database_url='sqlite:///database.db', detik_akses=900, origin_diizinkan=['http://localhost:3000'], secret_key=SecretStr('**********'))
```

Mencetak `secret_key` atau seluruh `Settings` (misalnya ke log) tidak membuka nilainya.

### Cache

Diuji: setelah `get_settings()` dipanggil sekali, mengubah `TUGASKU_NAMA_APLIKASI` di environment tidak mengubah hasil (`TugasKu` tetap `TugasKu`), dan dua panggilan mengembalikan objek yang sama. Untuk mengubah konfigurasi, mulai ulang server.

### Dokumentasi otomatis

Konfigurasi tidak muncul di `/openapi.json`, kecuali judul aplikasi. Tampilan Swagger UI **belum diverifikasi** lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Meng-commit `.env` | Rahasia masuk ke riwayat Git. `.env` ada di `.gitignore`; commit hanya `.env.contoh`. |
| Menaruh nilai rahasia sebagai nilai bawaan di kelas | Rahasia tertanam di kode. Biarkan tanpa nilai bawaan agar wajib diisi. |
| Mengembalikan `secret_key` di response | Rahasia bocor ke klien. Kembalikan hanya nilai aman. |
| Mencetak `Settings` ke log tanpa `SecretStr` | Rahasia tercatat di log (`SecretStr` mencegahnya; teruji). |
| Lupa awalan `TUGASKU_` | Variabel tidak terbaca dan field memakai nilai bawaan (atau error bila wajib). |
| Mengira mengubah environment langsung berpengaruh | `lru_cache` menyimpan hasil pertama (teruji). Mulai ulang server. |
| Membuat `Settings()` di setiap request | Berkas `.env` dibaca berulang. Pakai `lru_cache` (dokumentasi FastAPI). |
| Menjalankan dari folder lain | `.env` dicari di folder kerja, sehingga tidak ditemukan. Jalankan dari folder yang berisi `.env`. Tidak diuji di sini. |
| Menyimpan daftar di environment tanpa format JSON | Gagal dibaca sebagai `list`. Tulis sebagai teks JSON (teruji). |

## Latihan

1. **Dasar.** Variabel environment mana yang mengisi field `detik_akses`?
2. **Prediksi.** Apa yang terjadi bila `TUGASKU_DETIK_AKSES=10`? Kapan kesalahan itu muncul?
3. **Prediksi 2.** `.env` berisi `TUGASKU_DETIK_AKSES=1800`, tetapi environment juga berisi `TUGASKU_DETIK_AKSES=120`. Berapa nilai yang dipakai?
4. **Analisis.** Mengapa `secret_key` memakai `SecretStr` dan tidak diberi nilai bawaan?

??? success "Kunci jawaban"
    Jawaban 2 sampai 3 mengacu pada hasil uji di atas. Jawaban 1 dan 4 adalah penalaran dari kode dan hasil uji.

    1. `TUGASKU_DETIK_AKSES` (awalan dari `env_prefix`, nama field dalam huruf besar-kecil apa pun).
    2. `ValidationError` (`greater_than_equal`, minimal 60). Kesalahan muncul saat aplikasi mulai, bukan saat request pertama.
    3. 120. Environment mengalahkan `.env`.
    4. Tanpa nilai bawaan, aplikasi menolak mulai bila rahasia tidak diisi, sehingga tidak ada rahasia tertanam di kode. `SecretStr` mencegah nilai tercetak tak sengaja (teruji: `SecretStr('**********')`).

## Ringkasan

- Pisahkan konfigurasi dari kode: kode membaca, lingkungan menyediakan nilai.
- `BaseSettings` membaca environment dan `.env`, lalu mengonversi dan memvalidasi nilai dengan tipe dan `Field`.
- Prioritas: environment, lalu `.env`, lalu nilai bawaan.
- Field tanpa nilai bawaan wajib diisi; konfigurasi yang salah menggagalkan aplikasi sejak mulai.
- `SecretStr` menyembunyikan rahasia saat dicetak; jangan pernah mengembalikannya di response.
- `@lru_cache` membuat konfigurasi dibaca sekali; `.env` tidak di-commit, `.env.contoh` boleh.

## Langkah berikutnya

Lanjut ke [Middleware](middleware.md), atau kembali ke daftar materi di [Modul 08: Struktur Proyek](index.md).
