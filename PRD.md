# PRD — Dokumentasi Pembelajaran FastAPI (Bahasa Indonesia)

Status: Draft untuk persetujuan · Tanggal: 2026-10-26

PRD ini menggantikan PRD template MkDocs sebelumnya (masih tersedia di riwayat git, commit `5348860`).

## 1. Tujuan

Membangun situs dokumentasi pembelajaran **FastAPI berbahasa Indonesia** yang membawa pembaca dari pemula hingga tingkat lanjutan. Situs dibangun di atas template MkDocs + Material yang sudah ada di repository ini, tanpa mengganti stack-nya.

Keberhasilan diukur dari: pembaca dapat membangun, menguji, dan men-deploy API sendiri dengan mengikuti materi secara berurutan.

## 2. Target pembaca

| Kelompok | Karakteristik |
|---|---|
| Utama | Mahasiswa dan pemula yang sudah mengenal dasar Python, tetapi belum pernah membuat web API |
| Sekunder | Developer yang berpindah dari Flask/Django atau framework lain |
| Tingkat lanjut | Developer yang butuh referensi autentikasi, basis data, pengujian, dan deployment |

## 3. Prasyarat pembelajaran

- Dasar Python: variabel, fungsi, kondisi, perulangan, list/dict, class, import, dan type hints dasar.
- Mampu memakai terminal dan editor kode.
- Konsep HTTP secara umum (diperkenalkan ulang secara ringkas di Modul 1).
- SQL dasar dibutuhkan mulai modul basis data. Modul tersebut harus menyebut prasyarat ini di awal.

Materi tidak mengajarkan Python dari nol. Halaman awal harus menautkan sumber belajar Python bagi yang belum siap.

## 4. Learning outcomes

Setelah menyelesaikan seluruh kurikulum, pembaca mampu:

1. Menjelaskan peran HTTP, REST, dan ASGI dalam sebuah aplikasi FastAPI.
2. Membuat endpoint dengan path parameter, query parameter, dan request body.
3. Memvalidasi dan menserialisasi data menggunakan model Pydantic.
4. Mengelola error dan status code secara konsisten.
5. Menggunakan dependency injection untuk berbagi logika.
6. Menghubungkan aplikasi ke basis data dan mengelola skema.
7. Mengamankan API dengan autentikasi dan otorisasi.
8. Menulis pengujian otomatis untuk endpoint.
9. Menyusun proyek yang terstruktur dan men-deploy-nya.

## 5. Struktur kurikulum

Setiap modul adalah satu folder dengan `index.md` sebagai landing page. Daftar topik di bawah adalah **rencana**. Nama fungsi, parameter, dan perilaku FastAPI harus diverifikasi terhadap dokumentasi resmi dan versi terpasang sebelum ditulis (lihat §8).

| Modul | Tingkat | Topik utama |
|---|---|---|
| 01 Pengenalan | Pemula | Apa itu FastAPI, HTTP dan REST, instalasi dan venv, aplikasi pertama, menjalankan server, dokumentasi interaktif otomatis |
| 02 Dasar Routing | Pemula | Path parameter, query parameter, urutan route, dasar async/await. Path operation dan HTTP method sudah dibahas di Modul 01 |
| 03 Data dan Validasi | Pemula | Request body, model Pydantic, validasi field, validasi path dan query parameter (batasan nilai), response model, type hints |
| 04 Penanganan Error | Menengah | Status code, `HTTPException`, validasi error, handler kustom |
| 05 Dependency Injection | Menengah | Konsep dependency, dependency berantai, dependency per router |
| 06 Basis Data | Menengah | Koneksi, model dan skema, operasi CRUD, relasi, migrasi |
| 07 Autentikasi dan Keamanan | Menengah–Lanjut | Hashing password, token, proteksi endpoint, otorisasi, CORS |
| 08 Struktur Proyek | Lanjut | Router modular, konfigurasi dan environment, middleware, background task |
| 09 Pengujian | Lanjut | Pengujian endpoint, fixture, override dependency, basis data uji |
| 10 Deployment | Lanjut | Server produksi, container, variabel environment, logging, checklist rilis |

Urutan modul tidak boleh dilompati tanpa menyebut prasyaratnya. Topik async/await dibahas secara bertahap: konsep dasar di Modul 02, lalu penerapannya di modul basis data.

### Pola setiap bab

Mengikuti pola template (`docs/curriculum/index.md`):

1. Tujuan pembelajaran (daftar `[x]` yang terukur)
2. Konsep
3. Sintaks dan contoh kode
4. Output yang diharapkan
5. Tutorial langkah demi langkah
6. Kesalahan umum
7. Latihan
8. Ringkasan

## 6. Standar penyajian materi

- Bahasa Indonesia yang jelas untuk pemula. Istilah teknis dipertahankan dalam bahasa Inggris (misalnya *endpoint*, *request*), dijelaskan saat pertama muncul.
- Satu konsep baru per bagian. Definisikan istilah sebelum dipakai.
- **Setiap blok kode dijelaskan bagian demi bagian** setelah kode ditampilkan, dengan merujuk baris atau nama yang relevan.
- Gunakan fitur template yang sudah ada: tab, admonition, `title="..."`, anotasi kode, tabel, dan diagram Mermaid bila membantu.
- Judul halaman satu `# H1`; hierarki heading tidak melompat.
- Tidak menambahkan klaim tanpa dasar. Output yang ditampilkan harus berasal dari eksekusi nyata (lihat §8).

### Standar contoh kode

- Sumber kode berada di `examples/fastapi/<modul>/`, dipanggil dari halaman dengan `--8<-- "fastapi/<modul>/<file>.py"` (path relatif terhadap `examples/`, sesuai `pymdownx.snippets`).
- Satu contoh = satu file yang berdiri sendiri dan dapat dijalankan, kecuali kode memang potongan dari proyek praktik (ditandai jelas).
- Nama variabel dan fungsi dalam bahasa Inggris; komentar dan penjelasan dalam bahasa Indonesia.
- Type hints dipakai konsisten. Tidak ada secret nyata; gunakan nilai contoh yang jelas palsu.
- Versi Python, FastAPI, dan Pydantic yang dipakai dicatat di satu tempat (halaman Getting Started) dan di berkas dependensi contoh.

## 7. Proyek praktik bertahap

Satu proyek berkelanjutan, misalnya **API manajemen tugas (to-do)**. Judul final ditetapkan saat implementasi. Setiap tahap menambah fitur di atas hasil tahap sebelumnya.

| Tahap | Setelah modul | Hasil |
|---|---|---|
| 1 | 03 | CRUD dalam memori dengan model Pydantic |
| 2 | 04 | Validasi dan error terstruktur |
| 3 | 06 | Penyimpanan di basis data |
| 4 | 07 | Registrasi, login, dan endpoint yang dilindungi |
| 5 | 09 | Rangkaian pengujian otomatis |
| 6 | 10 | Dikemas dan siap deploy |

Kode proyek disimpan di `examples/fastapi/proyek/tahap-<n>/`. Tiap tahap harus dapat dijalankan sendiri.

## 8. Kriteria kualitas dan validasi teknis

**Akurasi**

- Setiap API, parameter, dan perilaku diverifikasi terhadap dokumentasi resmi FastAPI dan versi yang terpasang. Tidak boleh mengarang API.
- Setiap contoh kode dijalankan sebelum masuk ke materi. Output yang dicantumkan adalah output hasil eksekusi tersebut.
- Jika sesuatu tidak dapat diverifikasi, tandai dengan jelas atau jangan dicantumkan.

**Build**

- `mkdocs build --strict` harus lulus tanpa warning baru. Build ke direktori sementara bila tidak ingin menyentuh `site/`.
- Semua tautan internal dan anchor valid. Semua halaman terdaftar di `nav`.
- Snippet mengacu ke file yang ada (`check_paths: true`).

**Konten**

- Setiap bab memenuhi pola di §5 dan standar di §6.
- Setiap bab punya tujuan pembelajaran yang terukur dan minimal satu latihan.
- Dibaca ulang pada tampilan terang dan gelap serta lebar layar ponsel untuk memastikan tidak ada tabel atau kode yang terpotong.

**Pelaporan**

- Setiap perubahan dilaporkan dengan daftar file, hasil validasi, dan masalah yang tersisa. Bagian yang tidak diuji dinyatakan tidak diuji.

## 9. Integrasi ke navigasi MkDocs

Berdasarkan audit: navigasi di `mkdocs.yml` ditulis **manual**, dan halaman yang tidak terdaftar memicu warning `omitted_files` yang menggagalkan build `--strict`.

- Materi ditempatkan di `docs/curriculum/<nn-modul>/` dan didaftarkan di bawah bagian `Curriculum` pada `nav`.
- Setiap modul memiliki `index.md` sebagai landing page.
- Halaman `docs/curriculum/index.md` diperbarui menjadi daftar modul FastAPI.
- Contoh bentuk `nav`:

```yaml
nav:
  - Curriculum:
      - curriculum/index.md
      - 01 Pengenalan:
          - curriculum/01-pengenalan/index.md
          - Aplikasi Pertama: curriculum/01-pengenalan/aplikasi-pertama.md
```

- Menambahkan halaman = membuat file + menambah entri `nav` dalam perubahan yang sama.
- Halaman `authoring/` dan `examples/` bawaan template dipertahankan sampai ada keputusan lain.

## 10. Pekerjaan penyiapan situs (satu kali)

Ini dikerjakan terpisah dari penulisan materi, masing-masing sebagai perubahan tersendiri dengan alasan yang jelas:

- Memperbarui identitas di `mkdocs.yml`: `site_name`, `site_description`, `site_url`, `repo_url`, `repo_name`, `edit_uri`.
- Mengubah `theme.language` ke `id` setelah memeriksa dukungannya di Material, termasuk bahasa pencarian.
- Memutuskan nasib `TECHNICAL_DESIGN.md`, `VALIDATION_REPORT.md`, `PROMPT_MKDOCS_TEMPLATE.md`, dan `.shots$4.png` (dipertahankan, dipindahkan, atau dihapus).
- Menetapkan remote git tujuan sebelum `gh-deploy` pertama. Remote `origin` saat ini masih repo template.

## 11. Batasan ruang lingkup

**Termasuk:** materi tertulis, contoh kode, diagram, latihan, dan proyek praktik FastAPI dalam bahasa Indonesia.

**Tidak termasuk:**

- Pengajaran Python dari dasar.
- Mesin eksekusi kode atau playground interaktif di dalam situs.
- Perubahan tema, plugin, atau stack MkDocs di luar kebutuhan materi.
- Terjemahan ke bahasa lain dan situs multi-versi.
- Frontend, JavaScript, atau topik non-FastAPI selain yang diperlukan untuk konteks.
- CI/CD otomatis, kecuali diputuskan terpisah.
- Menjalankan commit, push, atau deploy tanpa persetujuan eksplisit.

## 12. Risiko dan keputusan terbuka

| Item | Keterangan |
|---|---|
| Versi FastAPI/Pydantic | Perlu ditetapkan dan dicatat sebelum menulis kode. Perubahan versi dapat membuat contoh tidak berlaku |
| Pilihan basis data dan library | SQLite dengan ORM tertentu, atau yang lain, diputuskan sebelum Modul 06 |
| Metode autentikasi | Diputuskan sebelum Modul 07 |
| Ukuran `nav` | Navigasi manual akan membesar; pantau keterbacaannya |
| Tanda `$` pada teks | Dapat dibaca sebagai LaTeX oleh MathJax. Di luar blok kode, tulis sebagai `\$` |
| Python 3.12 | Template baru diuji pada 3.14; kompatibilitas lain belum dibuktikan |
| Output contoh | Hanya dari eksekusi nyata; membutuhkan lingkungan uji yang dapat dijalankan |
