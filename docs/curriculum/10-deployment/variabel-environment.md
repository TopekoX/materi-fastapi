# Variabel Environment di Produksi

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan mengapa konfigurasi dan rahasia dipisahkan dari kode, dan dari image container.
- [ ] Mengatur sumber konfigurasi dan memahami urutan prioritasnya: argumen, environment, `.env`, berkas rahasia, nilai bawaan.
- [ ] Membedakan lingkungan (`pengembangan`, `uji`, `produksi`) dengan satu variabel.
- [ ] Menolak konfigurasi berbahaya di produksi saat aplikasi mulai.
- [ ] Membaca rahasia dari berkas (pola *Docker secrets*).
- [ ] Mengenali jebakan `.env` yang dipakai bersama alat lain (`extra="ignore"`).

## Prasyarat

- Sudah membaca [Konfigurasi dan Environment](../08-struktur-proyek/konfigurasi-environment.md) dan [Container](container.md).
- Sudah membaca [Token](../07-autentikasi-keamanan/token.md), terutama bagian kunci penandatangan.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **Pydantic 2.14.1**, **pydantic-settings 2.16.1**, **python-dotenv 1.2.4**, dan **pytest 9.1.1** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**. Perilaku Docker dan Kubernetes (misalnya cara mereka menyuntikkan variabel) **tidak diuji**.

## Konsep

Halaman [Konfigurasi dan Environment](../08-struktur-proyek/konfigurasi-environment.md) mengajarkan cara membaca konfigurasi. Halaman ini membahas apa yang berbeda di **produksi**:

| Di laptop | Di produksi |
|---|---|
| Kunci contoh boleh dipakai | Kunci harus acak, panjang, dan rahasia |
| `mode_debug` boleh menyala | Harus mati |
| CORS boleh longgar | Hanya origin frontend yang sah |
| `.env` di folder proyek | Tidak ada `.env` di image; nilai disuntikkan oleh lingkungan |
| Dokumentasi interaktif terbuka | Pertimbangkan menutupnya |

Tiga prinsip:

1. **Satu kode, banyak lingkungan.** Image atau kode yang sama dijalankan di mana saja; yang berbeda hanya konfigurasinya.
2. **Rahasia tidak masuk Git maupun image.** Container dan `Dockerfile` tidak menanamkan rahasia ([Container](container.md)).
3. **Gagal cepat dan jelas.** Konfigurasi yang salah atau berbahaya harus menggagalkan aplikasi saat mulai, bukan menunggu pengguna menemukan masalahnya.

### Urutan prioritas sumber

Menurut dokumentasi `pydantic-settings`, bila nilai bisa datang dari beberapa sumber, yang lebih awal menang:

1. argumen yang diberikan saat membuat `Settings(...)`,
2. variabel environment,
3. berkas `.env`,
4. berkas rahasia (`secrets_dir`),
5. nilai bawaan di kelas.

Dokumentasi menegaskan bahwa environment dan `.env` selalu lebih diutamakan daripada folder rahasia. `env_file` boleh berupa beberapa berkas; yang belakang menimpa yang depan.

Aturan praktis: nilai bawaan untuk hal yang aman; `.env` untuk kenyamanan di laptop; **variabel environment atau berkas rahasia untuk produksi**.

## Kode lengkap

Contoh ada di `examples/fastapi/10-deployment/variabel-environment/`.

### `config.py`

```python title="config.py"
--8<-- "fastapi/10-deployment/variabel-environment/config.py"
```

### `main.py`

```python title="main.py"
--8<-- "fastapi/10-deployment/variabel-environment/main.py"
```

### `.env.contoh`

```text title=".env.contoh"
--8<-- "fastapi/10-deployment/variabel-environment/.env.contoh"
```

### `test_konfigurasi.py`

```python title="test_konfigurasi.py"
--8<-- "fastapi/10-deployment/variabel-environment/test_konfigurasi.py"
```

## Penjelasan kode

### Satu variabel untuk lingkungan

```python
lingkungan: Literal["pengembangan", "uji", "produksi"] = "pengembangan"
```

`Literal` membatasi nilainya. Nilai yang tidak dikenal (misalnya `staging`) langsung menjadi `ValidationError` (teruji). Nilai bawaannya `pengembangan`. Perhatikan konsekuensinya: bila variabel ini lupa diisi di server, aturan produksi **tidak berlaku**. Karena itu server produksi harus selalu mengisi `TUGASKU_LINGKUNGAN=produksi` secara eksplisit; menjadikan `produksi` sebagai nilai bawaan adalah alternatif yang lebih aman, tetapi tidak dipakai di contoh ini.

### Aturan khusus produksi

```python
@model_validator(mode="after")
def periksa_aturan_produksi(self):
    if self.lingkungan == "produksi":
        masalah = []
        if self.mode_debug: masalah.append("mode_debug harus False")
        if "*" in self.origin_diizinkan: masalah.append("origin_diizinkan tidak boleh berisi '*'")
        if self.secret_key.get_secret_value().startswith(KUNCI_CONTOH): masalah.append("secret_key masih kunci contoh")
        if masalah:
            raise ValueError("Konfigurasi produksi tidak aman: " + "; ".join(masalah))
    return self
```

`model_validator(mode="after")` berjalan setelah semua field tervalidasi dan bisa memeriksa **gabungan** field. Di produksi, tiga hal ditolak: debug menyala, CORS berisi `*`, dan kunci contoh. Semua masalah dilaporkan sekaligus. Ini penerapan prinsip "gagal cepat": lebih baik aplikasi tidak mulai daripada berjalan dengan pengaturan yang tidak aman.

### Sumber konfigurasi

```python
model_config = SettingsConfigDict(env_prefix="TUGASKU_", env_file=(".env", ".env.lokal"), extra="ignore")
```

- `env_file` berisi dua berkas: `.env.lokal` menimpa `.env` (dokumentasi: yang belakang menimpa).
- `extra="ignore"`: lihat jebakan di bawah.

### Nama berkas rahasia

`Settings(_secrets_dir=...)` (atau `secrets_dir` di `model_config`) membaca rahasia dari **berkas**: nama berkas sama dengan nama field, dan `env_prefix` juga berlaku pada nama berkas. Contoh: rahasia `secret_key` dengan awalan `TUGASKU_` dibaca dari berkas `tugasku_secret_key`. Docker menyediakan rahasia sebagai berkas di `/run/secrets` (dokumentasi pydantic-settings); pola ini tidak diuji di dalam Docker.

### Mematikan dokumentasi di produksi

```python
docs_url=None if settings.lingkungan == "produksi" else "/docs",
openapi_url=None if settings.lingkungan == "produksi" else "/openapi.json",
```

Ini pilihan, bukan kewajiban: dokumentasi interaktif membantu pengembangan, tetapi di produksi ia memperlihatkan seluruh bentuk API kepada siapa pun.

## Menjalankan

Dari folder contoh:

```powershell
$env:TUGASKU_SECRET_KEY = (python -c "import secrets; print(secrets.token_hex(32))")
fastapi run main.py --host 127.0.0.1 --port 8000
```

Menjalankan pengujian:

```powershell
pytest
```

## Mencoba

### Pengujian: 17 lolos

Hasil sebenarnya: `17 passed`. Isinya:

| Kelompok | Yang dibuktikan |
|---|---|
| Dasar | rahasia wajib; lingkungan hanya nilai yang dikenal; nilai bawaan `pengembangan` |
| Aturan produksi | konfigurasi aman diterima; `mode_debug=true`, origin `["*"]`, dan kunci contoh masing-masing ditolak dengan pesan yang sesuai; hal yang sama **boleh** di pengembangan |
| Prioritas | `.env` dibaca; `.env.lokal` menimpa `.env`; variabel environment menang atas `.env`; berkas rahasia dibaca; environment menang atas berkas rahasia |
| Folder rahasia | folder yang tidak ada hanya memberi peringatan |
| `.env` bersama | entri lain diabaikan (`extra="ignore"`); pada pengaturan ketat ditolak; salah ketik nama terdeteksi hanya oleh pengaturan ketat |

### Server di pengembangan dan di produksi

Dengan `TUGASKU_SECRET_KEY` terisi (kunci 64 karakter):

| Lingkungan | `GET /info` | `GET /docs` | `GET /openapi.json` |
|---|---|---|---|
| `pengembangan` (bawaan) | `{"lingkungan":"pengembangan","mode_debug":false,"origin_diizinkan":["http://localhost:3000"],"panjang_secret_key":64}` | `200` | tidak diuji |
| `produksi` | `{"lingkungan":"produksi",...}` | `404` | `404` |

`GET /info` tidak pernah mengembalikan nilai kunci, hanya panjangnya.

### Produksi dengan debug menyala menolak mulai

```powershell
$env:TUGASKU_LINGKUNGAN = "produksi"; $env:TUGASKU_MODE_DEBUG = "true"
fastapi run main.py
```

Aplikasi tidak mulai:

```text
Value error, Konfigurasi produksi tidak aman: mode_debug harus False
```

### Dokumentasi otomatis

Selain pengaturan `docs_url` di atas, tampilan visual Swagger UI **belum diverifikasi** lewat browser.

## Jebakan: `.env` yang dipakai bersama alat lain

Bawaan `pydantic-settings` adalah `extra="forbid"`: entri apa pun di berkas `.env` yang tidak cocok dengan field menimbulkan `ValidationError`. Hasil sebenarnya pada percobaan pertama dengan `.env` berisi `PATH_LAIN=1` (tanpa awalan sama sekali):

```text
path_lain
  Extra inputs are not permitted [type=extra_forbidden, input_value='1', input_type=str]
```

Pada kenyataannya, `.env` sering dipakai bersama alat lain, misalnya Docker Compose (yang membaca `.env` untuk substitusi variabel, menurut dokumentasi Docker; tidak diuji di sini). Entri alat lain akan menggagalkan aplikasi. Contoh ini memakai `extra="ignore"`. Namun ada harganya, dan teruji:

| Pengaturan | `.env` berisi `COMPOSE_PROJECT_NAME=lain` | `.env` berisi `TUGASKU_LINGKUNAN=produksi` (salah ketik) |
|---|---|---|
| `extra="ignore"` | aman | **diam-diam diabaikan**: `lingkungan` tetap `pengembangan` |
| `extra="forbid"` (bawaan) | ditolak: `extra_forbidden` | ditolak: salah ketik terdeteksi |

Jadi `extra="ignore"` menukar keamanan terhadap salah ketik dengan toleransi terhadap `.env` bersama. Salah ketik pada variabel keamanan (`TUGASKU_LINGKUNAN`) bahkan bisa membuat aplikasi berjalan dalam mode yang salah tanpa peringatan. Pilihan lain (tidak diuji): memakai berkas `.env` khusus aplikasi, atau menyuntikkan variabel lewat environment dan tidak memakai `.env` sama sekali di produksi.

## Pola di produksi

| Cara | Kapan | Catatan |
|---|---|---|
| Variabel environment dari sistem | Server, container (`--env-file` atau `environment:`), layanan cloud | Paling umum; mudah diganti per lingkungan |
| Berkas rahasia (`secrets_dir`) | Docker secrets atau mekanisme serupa yang memasang rahasia sebagai berkas | Rahasia tidak muncul di daftar environment proses (alasan umum; tidak diuji) |
| `.env` | Laptop | Jangan di-commit; jangan masuk image (`.dockerignore`) |
| Pengelola rahasia khusus (cloud) | Organisasi yang memilikinya | `settings_customise_sources` memungkinkan menambah sumber seperti itu (dokumentasi pydantic-settings); tidak dibahas di sini |

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Meng-commit `.env` atau memasukkannya ke image | Rahasia bocor ke riwayat Git atau siapa pun yang memegang image. |
| Nilai bawaan rahasia di kode | Rahasia tertanam. Biarkan tanpa nilai bawaan agar wajib diisi. |
| `mode_debug` menyala di produksi | Ditolak oleh aturan produksi di contoh ini (teruji). |
| CORS berisi `*` di produksi | Ditolak oleh aturan produksi (teruji). |
| Salah ketik nama variabel dengan `extra="ignore"` | Diabaikan tanpa peringatan (teruji). |
| `.env` bersama alat lain dengan `extra="forbid"` | Aplikasi gagal mulai (teruji). |
| Mencetak seluruh `Settings` ke log | Aman bila rahasia memakai `SecretStr` (dibahas di Konfigurasi dan Environment); tidak aman bila tidak. |
| Mengembalikan rahasia di endpoint (misalnya `/info`) | Rahasia bocor ke klien. |
| Mengira perubahan environment langsung berlaku | `lru_cache` menyimpan hasil pertama. Mulai ulang aplikasi. |
| Menganggap `Literal` memvalidasi isian `.env` yang salah ketik nama | Hanya nilai yang divalidasi, bukan nama variabel. |

## Latihan

1. **Dasar.** Variabel mana yang menentukan lingkungan, dan nilai apa yang diterima?
2. **Prediksi.** `.env` berisi `TUGASKU_LINGKUNGAN=uji`, dan environment berisi `TUGASKU_LINGKUNGAN=produksi`. Lingkungan mana yang dipakai, dan mengapa?
3. **Praktik.** Tambahkan aturan produksi baru: `database_url` tidak boleh mengandung `sqlite`. Di mana kamu menaruhnya?
4. **Analisis.** Mengapa `extra="ignore"` bisa berbahaya pada variabel keamanan?

??? success "Kunci jawaban"
    Jawaban 1 sampai 4 mengacu pada hasil uji di atas, kecuali 3 yang merupakan penerapan pola dan tidak dijalankan.

    1. `TUGASKU_LINGKUNGAN`; nilainya `pengembangan`, `uji`, atau `produksi`. Nilai lain menimbulkan `ValidationError`.
    2. `produksi`: variabel environment menang atas `.env` (teruji pada `test_variabel_environment_menang_atas_berkas_env`).
    3. Di `periksa_aturan_produksi`, di dalam blok `if self.lingkungan == "produksi":`, dengan `if "sqlite" in self.database_url: masalah.append("database_url tidak boleh SQLite di produksi")`.
    4. Salah ketik nama variabel (`TUGASKU_LINGKUNAN`) diabaikan tanpa peringatan, sehingga aplikasi bisa berjalan dengan pengaturan bawaan alih-alih yang dimaksud (teruji: `lingkungan` tetap `pengembangan`).

## Ringkasan

- Satu kode untuk semua lingkungan; yang berbeda hanya konfigurasi, dan rahasia tidak masuk Git maupun image.
- Prioritas sumber: argumen, environment, `.env`, berkas rahasia, nilai bawaan; beberapa `env_file` ditimpa dari belakang.
- Satu variabel `lingkungan` (`Literal`) membedakan pengembangan, uji, dan produksi.
- `model_validator` menolak konfigurasi berbahaya di produksi (debug menyala, CORS `*`, kunci contoh) saat aplikasi mulai.
- Rahasia bisa dibaca dari berkas (`secrets_dir`), mengikuti pola Docker secrets.
- `extra="ignore"` mengatasi `.env` bersama, tetapi menyembunyikan salah ketik.

## Langkah berikutnya

Lanjut ke [Logging](logging.md), atau kembali ke daftar materi di [Modul 10: Deployment](index.md).
