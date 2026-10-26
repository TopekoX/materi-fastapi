# Belajar FastAPI

Dokumentasi pembelajaran **FastAPI berbahasa Indonesia**, dari pemula hingga mahir. Dibangun dengan [MkDocs](https://www.mkdocs.org/) dan [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/), dari template `TopekoX/mkdocs-template`.

Pembaca yang mengikuti materi secara berurutan akan membangun, menguji, dan mengemas satu API manajemen tugas (**TugasKu**) hingga siap di-deploy.

## Isi materi

Sepuluh modul di `docs/curriculum/`, ditambah [Peta Belajar](docs/peta-belajar.md) (urutan, prasyarat, dan proyek praktik).

| Modul | Topik | Tingkat |
|---|---|---|
| 01 Pengenalan | FastAPI, HTTP dan REST, instalasi, aplikasi pertama, dokumentasi interaktif | Pemula |
| 02 Dasar Routing | Path parameter, query parameter, urutan route, async/await | Pemula |
| 03 Data dan Validasi | Request body, model Pydantic, validasi, response model | Pemula |
| 04 Penanganan Error | Status code, `HTTPException`, error validasi, handler kustom | Menengah |
| 05 Dependency Injection | Dependency sederhana, berantai, `yield`, per router | Menengah |
| 06 Basis Data | SQLModel, CRUD, relasi, sesi async, migrasi Alembic | Menengah |
| 07 Autentikasi dan Keamanan | Hashing password, token, proteksi endpoint, otorisasi, CORS | Menengah–Lanjut |
| 08 Struktur Proyek | Router modular, konfigurasi, middleware, background task, lifespan | Lanjut |
| 09 Pengujian | Pengujian endpoint, fixture, override dependency, mock, async | Lanjut |
| 10 Deployment | Server produksi, container, variabel environment, logging, reverse proxy dan HTTPS, checklist rilis | Lanjut |

Proyek praktik berjalan dalam enam tahap (`examples/fastapi/proyek/tahap-1` sampai `tahap-6`), satu tahap setelah modul 03, 04, 06, 07, 09, dan 10.

Materi **tidak mengajarkan Python dari nol**. Halaman awal menautkan tutorial resmi Python bagi yang belum siap.

## Prinsip akurasi

- Kode contoh dijalankan sebelum masuk ke materi, dan keluaran yang ditampilkan berasal dari eksekusi nyata.
- Bagian yang tidak diuji ditandai di halaman terkait, bukan disembunyikan.
- Sebagian besar contoh dijalankan di Windows (PowerShell). Perintah Docker di Modul 10 dijalankan di Ubuntu dengan Docker Engine. macOS dan Docker Desktop belum diuji.
- Daftar versi yang dipakai ada di halaman [Instalasi dan Virtual Environment](docs/curriculum/01-pengenalan/instalasi-dan-venv.md) (bagian "Versi yang dipakai di materi ini").

## Menjalankan situs dokumentasi

Di Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
mkdocs serve                  # pratinjau di http://127.0.0.1:8000
mkdocs build --strict         # validasi; output ke site/
```

macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.

Untuk tidak mengisi `site/`, bangun ke direktori sementara: `mkdocs build --strict -d <direktori>`. Build `--strict` gagal bila ada tautan rusak, anchor tidak valid, atau halaman yang tidak terdaftar di `nav`.

Material for MkDocs menampilkan kotak pemberitahuan "MkDocs 2.0" pada setiap build. Itu pengumuman dari upstream, bukan error proyek, dan tidak menggagalkan `--strict`. `requirements.txt` membatasi `mkdocs<2`.

## Menjalankan kode contoh

Kode contoh FastAPI memakai lingkungan Python **terpisah** dari situs dokumentasi. Dependensinya terkunci di `examples/fastapi/requirements.txt`.

```powershell
python -m venv .venv-contoh
.venv-contoh\Scripts\Activate.ps1
pip install -r examples/fastapi/requirements.txt
```

Setiap contoh berada di `examples/fastapi/<modul>/<topik>/`, dan dijalankan dari foldernya sendiri:

```powershell
cd examples/fastapi/01-pengenalan/aplikasi-pertama
fastapi dev main.py
```

Pengujian dijalankan per folder, misalnya:

```powershell
cd examples/fastapi/proyek/tahap-6
python -m pytest
```

Beberapa contoh sengaja berisi kode yang salah (berkas `main_salah.py` dan sejenisnya, atau satu tes yang sengaja gagal di `09-pengujian/pengujian-endpoint`) untuk memperlihatkan masalahnya. Halaman terkait menjelaskannya.

Contoh Modul 07 dan `proyek/tahap-4` (satu berkas) memerlukan variabel environment `SECRET_KEY`; `proyek/tahap-4-modular`, `tahap-5`, dan `tahap-6` memerlukan `TUGASKU_SECRET_KEY`. Cara membuat kunci acak ada di halaman [Token](docs/curriculum/07-autentikasi-keamanan/token.md). Jangan memakai kunci contoh di produksi.

## Struktur repository

```
mkdocs.yml                  identitas situs, tema, nav (manual), ekstensi, aset
requirements.txt            dependensi build dokumentasi
PRD.md                      kebutuhan dan standar kurikulum
CLAUDE.md                   panduan kerja untuk Claude Code di repository ini
docs/                       semua halaman yang dipublikasikan
  index.md, peta-belajar.md
  curriculum/<nn-modul>/    satu folder per modul; index.md = landing page
  stylesheets/extra.css     penyesuaian tema (hanya variabel var(--md-*))
  javascripts/              konfigurasi MathJax dan Mermaid
  assets/vendor/mermaid/    Mermaid yang di-vendor (offline), beserta LICENSE
examples/                   sumber kode yang TIDAK dipublikasikan
  fastapi/<modul>/<topik>/  contoh per halaman
  fastapi/proyek/tahap-N/   proyek praktik TugasKu
  fastapi/requirements.txt  dependensi contoh
```

## Menulis atau mengubah materi

Aturan lengkap ada di `PRD.md` (§5–§9) dan `CLAUDE.md`. Ringkasnya:

- **Halaman baru:** buat `docs/curriculum/<nn-modul>/<nama>.md` (huruf kecil, tanda hubung) yang diawali satu `# Judul`, lalu daftarkan di `nav` pada `mkdocs.yml` **dalam perubahan yang sama**.
- **Pola bab:** tujuan pembelajaran, konsep, sintaks dan contoh, output yang diharapkan, tutorial langkah demi langkah, kesalahan umum, latihan, ringkasan.
- **Kode:** simpan di `examples/fastapi/<modul>/<topik>/` dan panggil dengan snippet, misalnya `--8<-- "fastapi/02-dasar-routing/path-parameter/main.py"` (path relatif terhadap `examples/`; path yang salah menggagalkan build). Setiap blok kode dijelaskan bagian demi bagian setelah ditampilkan.
- **Bahasa:** Indonesia yang jelas untuk pemula. Istilah teknis tetap dalam bahasa Inggris dan dijelaskan saat pertama muncul. Komentar dalam kode berbahasa Indonesia.
- **Akurasi:** jangan mengarang API, parameter, atau keluaran. Verifikasi terhadap dokumentasi resmi dan versi yang terpasang, dan tulis keluaran hanya dari eksekusi nyata.
- **LaTeX (MathJax):** `$...$` atau `\(...\)` untuk inline, `$$...$$` atau `\[...\]` untuk blok. Tanda `$` literal di luar blok kode ditulis `\$`.
- **Diagram:** fence ` ```mermaid `.

Fitur template yang dipakai di materi: mode sistem/terang/gelap, tab, admonition, tombol salin kode, anotasi kode, daftar centang, tabel, grid cards, breadcrumbs, navigasi sebelumnya/berikutnya, dan pencarian.

## Ketergantungan jaringan saat dibuka

| Dependensi | Kapan | Catatan |
|---|---|---|
| `cdn.jsdelivr.net` (MathJax 3.2.2) | setiap halaman | diperlukan untuk persamaan; tanpa jaringan, rumus tidak tampil |
| Google Fonts | tidak pernah | `theme.font: false` memakai font sistem |
| Mermaid | tidak pernah | sudah di-vendor |

## Deploy

Belum ada yang di-deploy. Sebelum `mkdocs gh-deploy` pertama:

1. Tentukan repository tujuan. `origin` saat ini masih repo template, sehingga deploy dapat menimpa branch `gh-pages` milik orang lain.
2. Pastikan `site_url` di `mkdocs.yml` cocok dengan alamat Pages tujuan (`https://<user>.github.io/<repo>/`).
3. Jalankan `mkdocs build --strict` dan periksa hasilnya di mode terang, gelap, dan lebar ponsel.
4. Setelah disetujui: `mkdocs gh-deploy --strict`, lalu di GitHub atur **Settings → Pages → Deploy from a branch → `gh-pages` / root**.

## Lisensi

[MIT License](LICENSE). Pustaka Mermaid yang di-vendor di `docs/assets/vendor/mermaid/` juga berlisensi MIT dan menyertakan berkas `LICENSE`-nya sendiri.
