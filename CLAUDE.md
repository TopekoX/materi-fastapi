# CLAUDE.md

Repository ini adalah dokumentasi pembelajaran **FastAPI berbahasa Indonesia** untuk pemula hingga mahir. Dibangun dari template MkDocs + Material (`TopekoX/mkdocs-template`).

## Cara memakai dokumen ini

- Baca `PRD.md` **hanya** bila tugas menyangkut struktur kurikulum, standar materi, proyek praktik, atau cakupan. Untuk perbaikan kecil (typo, tautan, satu paragraf), tidak perlu.
- Jika PRD dan kondisi repository berbeda, ikuti kondisi aktual repository, lalu laporkan perbedaannya.
- Jangan menebak struktur. Periksa dulu dengan `Glob`/`Grep` atau baca file terkait.

## Struktur repository (aktual)

- `mkdocs.yml` — konfigurasi utama: identitas, tema, `nav` (manual), ekstensi, aset.
- `requirements.txt` — dependensi build dokumentasi (`mkdocs<2`, `mkdocs-material<10`, `pymdown-extensions`).
- `docs/` — semua halaman yang dipublikasikan.
  - `docs/curriculum/` — lokasi materi FastAPI (satu folder per modul, `index.md` sebagai landing page).
  - `docs/authoring/`, `docs/examples/`, `docs/getting-started/` — referensi bawaan template.
  - `docs/javascripts/` (`mathjax.js`, `mermaid-config.js`), `docs/stylesheets/extra.css`, `docs/assets/vendor/mermaid/` — aset template.
- `examples/` — sumber kode yang **tidak dipublikasikan**, dipanggil dari halaman lewat snippet. Kode FastAPI ada di `examples/fastapi/`.
- `site/` dan `.venv/` diabaikan git. Jangan di-commit.

## Fitur template yang harus dipertahankan

- Mode sistem/terang/gelap (palette Material).
- MathJax untuk LaTeX (`\(...\)`, `\[...\]`, `$...$`, `$$...$$`). Tanda `$` literal ditulis `\$` di luar blok kode.
- Diagram Mermaid (di-vendor, bisa offline) lewat fence ` ```mermaid `.
- Tab, admonition, tombol salin kode, anotasi kode, tasklist, tabel, grid cards, breadcrumbs, prev/next, pencarian.
- Snippet: `--8<-- "fastapi/<modul>/<file>.py"` (path relatif terhadap `examples/`; path yang salah menggagalkan build).
- CSS khusus hanya memakai variabel `var(--md-*)`.

## Aturan konfigurasi

- Jangan ubah `mkdocs.yml` selain `nav` dan, bila perlu, metadata situs. Perubahan tema, plugin, ekstensi, atau aset global hanya dengan alasan yang jelas, dan jelaskan alasannya di laporan.
- Jangan ubah `docs/assets/vendor/`, `docs/javascripts/`, atau `extra.css` untuk kebutuhan materi biasa.
- Jangan mengubah dependensi di `requirements.txt` tanpa alasan.
- Jangan melakukan commit, push, atau `mkdocs gh-deploy` kecuali diminta eksplisit. `origin` saat ini masih repo template, jadi deploy dapat menimpa `gh-pages` milik orang lain.
- Jangan menghapus berkas bawaan template (mis. `TECHNICAL_DESIGN.md`) tanpa instruksi.

## Menambah halaman

1. Buat `docs/curriculum/<nn-modul>/<nama>.md`, diawali satu `# Judul`.
2. Daftarkan di `nav` pada `mkdocs.yml` di perubahan yang sama. Halaman yang tidak terdaftar menggagalkan `mkdocs build --strict`.
3. Taruh kode di `examples/fastapi/<modul>/` dan panggil dengan snippet.
4. Gunakan nama file huruf kecil dengan tanda hubung.

## Standar penulisan materi

- Seluruh materi dalam **bahasa Indonesia** yang jelas untuk pemula. Istilah teknis tetap dalam bahasa Inggris dan dijelaskan saat pertama muncul.
- Satu konsep baru per bagian; definisikan istilah sebelum dipakai.
- Pola bab: tujuan pembelajaran, konsep, sintaks dan contoh, output yang diharapkan, tutorial langkah demi langkah, kesalahan umum, latihan, ringkasan.
- **Setiap blok kode wajib dijelaskan bagian demi bagian** setelah ditampilkan.
- Contoh kode: berdiri sendiri, memakai type hints, komentar berbahasa Indonesia, tanpa secret nyata.
- Jangan menambahkan konten di luar ruang lingkup PRD (mis. mengajar Python dari nol).

## Akurasi (penting)

- **Jangan mengarang API, parameter, perilaku, output program, atau hasil pengujian.**
- Verifikasi API FastAPI/Pydantic terhadap dokumentasi resmi dan versi yang benar-benar terpasang (`pip show`, `help()`, atau dokumentasi resmi).
- Output yang ditulis di materi harus berasal dari eksekusi nyata. Bila kode belum dijalankan, jangan tulis outputnya; katakan bahwa belum diverifikasi.
- Bila tidak yakin, tandai dengan jelas atau tanyakan. Jangan menutupnya dengan klaim yang terdengar meyakinkan.

## Perintah

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
mkdocs serve                  # preview di http://127.0.0.1:8000
mkdocs build --strict         # validasi; output ke site/
```

Untuk menghindari mengisi `site/`, build ke direktori sementara dengan `mkdocs build --strict -d <direktori>`. Notifikasi "MkDocs 2.0" saat build berasal dari upstream dan bukan error.

Kode contoh FastAPI dijalankan di venv terpisah. Dependensinya dicatat di `examples/fastapi/requirements.txt`, bukan di `requirements.txt` utama.

## Validasi sesuai cakupan perubahan

- Mengubah atau menambah halaman atau `nav`: jalankan `mkdocs build --strict` dan pastikan tidak ada warning baru.
- Menambah atau mengubah kode contoh: jalankan kode tersebut, uji endpoint-nya, dan bandingkan hasilnya dengan yang ditulis di materi.
- Perubahan hanya pada teks tanpa kode atau tautan: baca ulang, build cukup sekali di akhir.
- Jangan menjalankan validasi yang tidak relevan, tetapi jangan melaporkan sesuatu sebagai lulus bila tidak dijalankan.

## Cara bekerja

- Kerjakan hanya file yang relevan dengan tugas. Jangan merapikan, memformat ulang, atau mengubah file lain.
- Baca file sebelum mengubahnya. Jangan membuat file duplikat bila sudah ada.
- Ikuti gaya penulisan, penamaan, dan format file di sekitarnya.
- Jangan mencetak isi file besar secara penuh (mis. `mermaid.min.js`).

## Laporan akhir

Setiap tugas diakhiri laporan singkat:

1. **File yang berubah** — daftar, dengan satu baris per file.
2. **Hasil validasi** — perintah yang dijalankan dan hasil sebenarnya (lulus/gagal/tidak dijalankan).
3. **Masalah tersisa** — warning, keterbatasan, bagian yang belum diverifikasi, dan keputusan yang menunggu pemilik repo.
