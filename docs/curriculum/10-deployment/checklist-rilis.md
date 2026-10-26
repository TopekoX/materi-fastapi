# Checklist Rilis

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan fungsi checklist rilis dan membedakan item yang bisa diperiksa mesin dari yang harus diputuskan manusia.
- [ ] Menelusuri setiap item checklist ke bab yang membahasnya.
- [ ] Menjalankan `periksa_rilis.py` untuk menyaring kesalahan umum pada sebuah proyek.
- [ ] Membaca hasil `LULUS`, `GAGAL`, dan `LEWAT`, dan memahami batas pemeriksa otomatis.
- [ ] Menyusun checklist sendiri sebelum rilis.

## Prasyarat

- Sudah membaca [Server Produksi](server-produksi.md), [Container](container.md), [Variabel Environment](variabel-environment.md), dan [Logging](logging.md).

!!! info "Versi yang diuji"
    Skrip dan pengujian di halaman ini dijalankan dengan **Python 3.14.7** dan **pytest 9.1.1** di Windows (pytest-cov 7.1.0 untuk cakupan). Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Skrip hanya memakai pustaka standar Python. Sistem operasi lain **belum diuji**.

## Konsep

*Checklist rilis* adalah daftar pemeriksaan yang dilakukan setiap kali aplikasi akan dirilis ke produksi. Pilot pesawat memakai checklist bukan karena lupa cara terbang, tetapi karena orang yang ahli pun bisa melewatkan satu langkah saat terburu-buru. Hal yang sama berlaku untuk rilis.

Item checklist terbagi dua jenis:

| Jenis | Contoh | Cara memeriksa |
|---|---|---|
| **Bisa diperiksa mesin** | `.env` ada di `.gitignore`; versi dependensi dikunci | Skrip membaca berkas |
| **Perlu keputusan manusia** | Apakah `/docs` boleh terbuka? Siapa yang dihubungi bila gagal? | Orang yang bertanggung jawab |

Halaman ini memberi keduanya: daftar lengkap yang ditautkan ke bab asalnya, dan skrip kecil untuk item yang bisa diperiksa mesin.

## Checklist

Setiap item memuat bab tempat ia dibahas. Kolom **Otomatis** menunjukkan apakah `periksa_rilis.py` ikut memeriksanya.

### Rahasia dan konfigurasi

| Item | Bab | Otomatis |
|---|---|---|
| Kunci penandatangan token berasal dari environment/secret, bukan dari kode | [Variabel Environment](variabel-environment.md) | Sebagian (mendeteksi nilai tertulis di kode) |
| Kunci acak dan panjang, bukan kunci contoh | [Variabel Environment](variabel-environment.md) | Tidak (diperiksa saat aplikasi mulai) |
| `.env` dan `*.db` ada di `.gitignore` | [Konfigurasi dan Environment](../08-struktur-proyek/konfigurasi-environment.md) | Ya |
| `lingkungan = produksi`; mode debug mati | [Variabel Environment](variabel-environment.md) | Tidak |
| CORS hanya mengizinkan origin frontend yang sah, bukan `*` | [CORS](../07-autentikasi-keamanan/cors.md) | Sebagian (mendeteksi `allow_origins=["*"]` di kode) |
| Keputusan tentang `/docs` dan `/openapi.json`: terbuka atau ditutup | [Variabel Environment](variabel-environment.md) | Tidak |

### Aplikasi

| Item | Bab | Otomatis |
|---|---|---|
| Pengujian ada dan lulus; cakupan dilihat | [Pengujian Endpoint](../09-pengujian/pengujian-endpoint.md) | Hanya keberadaannya |
| Migrasi basis data ada dan sudah diuji pada salinan data | [Migrasi](../06-basis-data/migrasi.md) | Hanya keberadaan `alembic.ini` |
| Basis data produksi bukan SQLite berkas yang tidak dicadangkan | [Koneksi ke Basis Data](../06-basis-data/koneksi-basis-data.md) | Tidak |
| Status penting tidak disimpan di memori proses | [Server Produksi](server-produksi.md) | Tidak |
| Log tidak memuat rahasia; level bukan `DEBUG` | [Logging](logging.md) | Tidak |

### Container dan server

| Item | Bab | Otomatis |
|---|---|---|
| Versi dependensi dikunci (`==`) | [Container](container.md) | Ya |
| `.dockerignore` menutup `.env` | [Container](container.md) | Ya |
| Container berjalan sebagai pengguna non-root | [Container](container.md) | Ya |
| Tidak ada rahasia di `Dockerfile` dan Compose | [Container](container.md) | Ya (heuristik) |
| Data ada di volume, bukan di dalam container | [Container](container.md) | Tidak |
| Jumlah worker dipilih dan diukur | [Server Produksi](server-produksi.md) | Tidak |
| HTTPS dihentikan di proksi dan header proksi dipercaya dengan benar | [Server Produksi](server-produksi.md), [Reverse Proxy dan HTTPS](reverse-proxy-https.md) | Tidak |

### Operasional

| Item | Keterangan | Otomatis |
|---|---|---|
| Ada cara memeriksa aplikasi hidup (*health check*) | Endpoint sederhana yang bisa dipanggil proksi atau orkestrator; contoh Compose di [Reverse Proxy dan HTTPS](reverse-proxy-https.md) | Tidak |
| Ada cadangan basis data dan cara memulihkannya | Dicoba memulihkan, bukan hanya membuat cadangan | Tidak |
| Ada rencana mundur (*rollback*) | Versi sebelumnya masih tersedia | Tidak |
| Ada yang dihubungi bila rilis bermasalah | Orang dan saluran yang jelas | Tidak |

!!! note "Daftar ini adalah titik awal"
    Item operasional di atas adalah praktik umum, bukan sesuatu yang diuji dalam materi ini. Sesuaikan dengan tempat kamu merilis.

## Kode lengkap

Contoh ada di `examples/fastapi/10-deployment/checklist-rilis/`.

### `periksa_rilis.py`

```python title="periksa_rilis.py"
--8<-- "fastapi/10-deployment/checklist-rilis/periksa_rilis.py"
```

## Penjelasan kode

- **`Hasil`** adalah tupel bernama berisi nama pemeriksaan, status (`LULUS`, `GAGAL`, atau `LEWAT`), dan catatan singkat. `LEWAT` berarti pemeriksaan tidak berlaku, misalnya tidak ada `Dockerfile` sehingga `.dockerignore` tidak perlu diperiksa.
- **`berkas_python`** mengumpulkan berkas `.py` aplikasi dengan mengabaikan lingkungan virtual, `alembic`, dan berkas pengujian. Berkas pengujian dikecualikan karena wajar memuat kata sandi palsu.
- **`cari_gitignore`** naik hingga lima tingkat folder untuk menemukan `.gitignore`, karena contoh berada di dalam repositori yang `.gitignore`-nya ada di akar.
- **`baris_aktif`** membaca baris yang bukan kosong dan bukan komentar, supaya `# .env` tidak dianggap sebagai aturan.
- **Fungsi `periksa_*`** masing-masing memeriksa satu item dan mengembalikan satu `Hasil`. Pemeriksaan rahasia memakai ekspresi reguler yang mencari nama seperti `secret`, `password`, `kata_sandi`, atau `api_key` yang diberi nilai teks sepanjang minimal enam karakter. Nilai berbentuk `${...}` di Compose dianggap rujukan variabel, bukan rahasia.
- **`PEMERIKSA`** adalah daftar semua pemeriksaan; menambah item berarti menulis fungsi dan menambahkannya ke daftar ini.
- **`main`** mencetak satu baris per pemeriksaan dan mengembalikan kode keluar `1` bila ada yang gagal, `0` bila tidak, dan `2` bila argumen salah. Kode keluar ini memungkinkan skrip dipakai di CI untuk menghentikan rilis.

!!! warning "Ini penyaring, bukan jaminan"
    Skrip hanya membaca teks. Ia tidak menjalankan aplikasi, Docker, atau pengujian. `LULUS` berarti pola buruk yang dicari tidak ditemukan, bukan berarti proyek aman. Rahasia dengan nama tak terduga, atau konfigurasi yang salah tetapi tertulis rapi, tidak akan terdeteksi.

## Menjalankan

Dari folder `examples/fastapi/10-deployment/checklist-rilis`:

```powershell
python periksa_rilis.py ..\..\proyek\tahap-5
```

Keluaran nyata (jalur `.gitignore` dipersingkat):

```text
[LULUS] .env dan *.db diabaikan Git - .gitignore
[LEWAT] .dockerignore menutup .env - tidak ada Dockerfile
[LEWAT] container berjalan sebagai non-root - tidak ada Dockerfile
[LULUS] tidak ada rahasia di Dockerfile/Compose - bersih
[GAGAL] versi dependensi dikunci (==) - tidak ada requirements.txt di folder ini
[LULUS] CORS tidak memakai '*' di kode - tidak ditemukan
[LULUS] tidak ada rahasia tertulis di kode - tidak ditemukan
[LULUS] ada pengujian - berkas test_*.py ditemukan
[LULUS] ada konfigurasi migrasi (Alembic) - alembic.ini ada

1 gagal dari 9 pemeriksaan
```

Kode keluarnya `1`. Artinya Proyek Tahap 5 belum siap dirilis: ia belum punya `requirements.txt` yang dikunci, dan belum punya `Dockerfile`. Itulah yang dikerjakan di [Container](container.md) dan [Proyek Praktik Tahap 6](proyek-tahap-6.md).

Hasil pemeriksaan untuk Tahap 6, yang sudah punya `Dockerfile`, `.dockerignore`, dan `requirements.txt`, ada di [Proyek Praktik Tahap 6](proyek-tahap-6.md#penilaian-kesiapan).

### Pelajaran dari percobaan pertama

Pada percobaan pertama, pemeriksa rahasia menandai Tahap 5 `GAGAL` pada `auth.py` baris 45. Penyebabnya ternyata `Token(..., token_type="bearer")`: kata `token` cocok dengan pola, padahal `"bearer"` bukan rahasia (hasil positif palsu). Kata `token` dikeluarkan dari pola pemeriksaan kode dan ditambahkan pengujian `test_token_type_bukan_rahasia`. Pemeriksa heuristik akan selalu punya positif palsu dan negatif palsu; jangan percaya buta pada hasilnya, baik `LULUS` maupun `GAGAL`.

## Pengujian

```powershell
python -m pytest -q
```

Hasil nyata:

```text
16 passed in 0.23s
```

Cakupan cabang (`--cov=periksa_rilis --cov-branch`) bernilai 92%. Baris yang belum tercakup: pelewatan folder lingkungan virtual, kasus tanpa `.gitignore`, kasus tanpa `requirements.txt`, dan blok `if __name__ == "__main__"`.

Pengujian membuat proyek palsu di folder sementara (`tmp_path`), memastikan proyek yang baik `LULUS` semua, lalu merusaknya satu per satu dan memastikan pemeriksaan yang sesuai `GAGAL`. Pengujian juga memeriksa kasus `LEWAT` dan kode keluar `main`.

## Kesalahan umum

| Kesalahan | Penjelasan |
|---|---|
| Menjalankan checklist hanya sekali di awal | Jalankan setiap rilis; konfigurasi berubah seiring waktu. |
| Mengandalkan skrip otomatis saja | Item penting seperti keputusan `/docs` dan cadangan butuh manusia. |
| Menganggap `LULUS` berarti aman | Skrip mencari pola yang dikenal saja. |
| Mengabaikan `LEWAT` | Pastikan memang tidak berlaku, bukan karena berkas salah tempat. |
| Menambah item tanpa pernah mengujinya | Item otomatis harus punya pengujian yang membuktikan ia bisa gagal. |
| Checklist tidak diperbarui setelah insiden | Setiap insiden yang bisa dicegah layak menjadi item baru. |

## Latihan

1. **Dasar.** Sebutkan dua item yang bisa diperiksa mesin dan dua yang harus diputuskan manusia.
2. **Prediksi.** Apa kode keluar `periksa_rilis.py` bila satu pemeriksaan `GAGAL`, dan bila semuanya `LULUS` atau `LEWAT`?
3. **Praktik.** Tambahkan pemeriksaan `periksa_healthcheck` yang `LULUS` bila ada berkas `.py` aplikasi yang memuat `"/health"`. Tambahkan juga ke `PEMERIKSA` dan tulis dua pengujian (ada dan tidak ada).
4. **Analisis.** Beri satu contoh rahasia yang lolos dari `periksa_rahasia_di_kode`.

??? success "Kunci jawaban"
    1. Mesin: `.env` di `.gitignore`, versi dependensi dikunci. Manusia: apakah `/docs` terbuka, siapa yang dihubungi bila rilis bermasalah.
    2. `1` bila ada yang `GAGAL`; `0` bila semuanya `LULUS` atau `LEWAT` (teruji pada `test_main_kode_keluar`).
    3. Penerapan pola yang sama dengan fungsi lain; tidak dijalankan di halaman ini. Kerangka: baca `berkas_python(folder)` dan cek `'"/health"' in teks`, kembalikan `Hasil("ada health check", "LULUS" atau "GAGAL", ...)`.
    4. Misalnya `kunci = "abc"` (nama tidak ada di daftar), atau nilai yang dirakit dari dua bagian string. Nama `token` juga sengaja tidak diperiksa (lihat bagian pelajaran di atas).

## Ringkasan

- Checklist rilis mencegah langkah yang terlewat; sebagian bisa diperiksa mesin, sebagian harus diputuskan manusia.
- Setiap item ditautkan ke bab asalnya, supaya alasan di baliknya mudah dibuka kembali.
- `periksa_rilis.py` memeriksa sembilan hal lewat pembacaan berkas dan mengembalikan kode keluar yang bisa dipakai di CI.
- Hasil heuristik bisa salah (positif dan negatif palsu), jadi `LULUS` bukan jaminan.
- Pada Tahap 5, pemeriksa menemukan 1 kegagalan nyata: belum ada dependensi yang dikunci.

## Langkah berikutnya

Lanjut ke [Proyek Praktik Tahap 6](proyek-tahap-6.md), atau kembali ke daftar materi di [Modul 10: Deployment](index.md).
