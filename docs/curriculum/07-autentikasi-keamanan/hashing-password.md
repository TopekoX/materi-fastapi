# Hashing Password

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan mengapa kata sandi tidak boleh disimpan apa adanya.
- [ ] Membedakan hashing dari enkripsi.
- [ ] Menjelaskan fungsi *salt* dan mengapa dua hash dari kata sandi yang sama berbeda.
- [ ] Meng-hash dan memverifikasi kata sandi dengan `pwdlib` (Argon2).
- [ ] Membuat endpoint pendaftaran yang tidak pernah mengembalikan kata sandi atau hash-nya.
- [ ] Menjelaskan fungsi hash tiruan untuk pengguna yang tidak ada.

## Prasyarat

- Sudah membaca [Response Model](../03-data-validasi/response-model.md) dan [HTTPException](../04-penanganan-error/http-exception.md).
- Dasar kata sandi dan akun pengguna sebagai pengguna aplikasi.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **pwdlib 0.3.1**, dan **argon2-cffi 25.1.0** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

!!! note "Pilihan pustaka untuk Modul 07"
    Modul ini memakai **pwdlib** dengan algoritma **Argon2**, sesuai tutorial keamanan di dokumentasi resmi FastAPI. Dokumentasi itu menyebut Argon2 sebagai algoritma yang direkomendasikan, dan menyebut `passlib` hanya untuk menangani hash lama (*legacy*).

## Konsep

### Mengapa tidak menyimpan kata sandi apa adanya

Bayangkan basis data aplikasimu bocor. Kalau kata sandi tersimpan apa adanya, penyerang langsung mendapat semuanya, dan karena banyak orang memakai kata sandi yang sama di banyak tempat, akun mereka di layanan lain ikut terancam. Aplikasi yang baik **tidak pernah menyimpan kata sandi asli**, bahkan pemiliknya sendiri tidak boleh bisa membacanya.

### Hashing, bukan enkripsi

| | Enkripsi | Hashing |
|---|---|---|
| Arah | Dua arah: bisa dibuka kembali dengan kunci | Satu arah: tidak bisa dikembalikan |
| Tujuan | Menyembunyikan data yang nanti perlu dibaca | Menyimpan "sidik jari" data |
| Untuk kata sandi | Tidak cocok | **Cocok** |

Fungsi *hash* mengubah kata sandi menjadi deretan karakter. Saat login, kita tidak membandingkan kata sandi asli. Kita meng-hash kata sandi yang diketik pengguna, lalu mencocokkannya dengan hash yang tersimpan.

### Salt dan kelambatan yang disengaja

Dua hal membuat hash kata sandi aman:

- **Salt**: data acak yang ditambahkan sebelum hashing, berbeda untuk setiap hash. Akibatnya dua pengguna dengan kata sandi yang sama tetap menghasilkan hash yang berbeda, dan penyerang tidak bisa memakai tabel hash siap pakai.
- **Kelambatan**: algoritma khusus kata sandi seperti Argon2 sengaja dibuat lambat dan memakan memori, supaya menebak miliaran kemungkinan menjadi mahal bagi penyerang. Bagi satu pengguna yang login, jedanya nyaris tak terasa.

Jangan memakai algoritma hash umum yang cepat (misalnya SHA-256 biasa) untuk kata sandi. Pustaka seperti `pwdlib` sudah memilihkan algoritma yang tepat dan menangani salt secara otomatis.

### Pemasangan

```powershell
pip install "pwdlib[argon2]"
```

Tanda kutip diperlukan di PowerShell karena ada tanda kurung siku.

## Mencoba dasarnya

Simpan sebagai `dasar_hash.py`:

```python title="dasar_hash.py"
--8<-- "fastapi/07-autentikasi-keamanan/hashing-password/dasar_hash.py"
```

Jalankan:

```powershell
python dasar_hash.py
```

Hasil sebenarnya (nilai hash berbeda setiap kali dijalankan):

```text
hash 1 : $argon2id$v=19$m=65536,t=3,p=4$bZcSmlYbrZ+kqmCCscAsAg$gpWD4e44d+KuAKIAfFOAC5ikhlQJwzu6cDscyUt2rtE
hash 2 : $argon2id$v=19$m=65536,t=3,p=4$c2X3nmmOZHPyNLrXnZGaJA$peIy5LMEfDUVL5oKkU1m3QY4sNTCQy0/C0GVfnwXD/4
kedua hash sama? False
kata sandi benar : True
kata sandi salah : False
verifikasi hash 2: True
waktu 1 kali hash: 37 ms
perlu hash ulang? False
```

### Penjelasan

- `PasswordHash.recommended()` membuat pengaturan yang direkomendasikan `pwdlib`. Hasil hash berawalan `$argon2id$`, yang menyebut algoritma dan parameternya.
- **Kedua hash berbeda** walau kata sandinya sama, karena salt acak tertanam di dalam hash (bagian setelah `p=4$`).
- `verify(kata_sandi, hash)` mengembalikan `True` atau `False`. Kedua hash tadi sama-sama lolos verifikasi untuk kata sandi yang benar.
- Satu kali hash memakan 37 ms pada mesin uji. Angka ini bergantung pada perangkat; jangan menganggapnya patokan.
- `verify_and_update` dipakai bila pengaturan algoritma suatu hari diubah: ia memeriksa kata sandi sekaligus melaporkan apakah hash perlu dibuat ulang. Di sini hasilnya `False` karena hash masih sesuai pengaturan. Penerapannya tidak dibahas lebih jauh.

## Kode lengkap

Berikut aplikasi FastAPI-nya. Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/07-autentikasi-keamanan/hashing-password/main.py"
```

## Penjelasan kode

### Hash tiruan

```python
password_hash = PasswordHash.recommended()
HASH_TIRUAN = password_hash.hash("kata-sandi-tiruan")
```

`password_hash` dibuat sekali dan dipakai ulang. `HASH_TIRUAN` dipakai pada endpoint pemeriksaan, dijelaskan di bawah.

### Tiga model

- `PenggunaBaru`: data masuk saat mendaftar, dengan aturan panjang. `kata_sandi` minimal 8 dan maksimal 128 karakter.
- `PenggunaPublik`: data keluar, **hanya** `nama_pengguna`. Tidak ada kata sandi maupun hash.
- `Kredensial`: nama dan kata sandi untuk pemeriksaan.

Pemisahan input dan output ini sama dengan [Response Model](../03-data-validasi/response-model.md): kata sandi mengalir masuk, tetapi tidak pernah keluar.

### Pendaftaran

```python
pengguna_db[data.nama_pengguna] = password_hash.hash(data.kata_sandi)
```

Yang disimpan adalah **hash**, bukan kata sandi. `pengguna_db` hanyalah `dict` di memori agar halaman fokus pada hashing; basis data nyata dipakai di proyek tahap 4. Nama yang sudah dipakai dijawab `409`.

### Pemeriksaan kata sandi

```python
hash_tersimpan = pengguna_db.get(data.nama_pengguna)
if hash_tersimpan is None:
    password_hash.verify(data.kata_sandi, HASH_TIRUAN)
    raise HTTPException(status_code=401, detail="Nama pengguna atau kata sandi salah")
if not password_hash.verify(data.kata_sandi, hash_tersimpan):
    raise HTTPException(status_code=401, detail="Nama pengguna atau kata sandi salah")
```

Dua keputusan penting:

1. **Pesan yang sama** untuk "nama tidak ada" dan "kata sandi salah". Dengan pesan berbeda, penyerang bisa menebak nama pengguna yang terdaftar.
2. **`verify` pada hash tiruan** bila nama tidak ada. Verifikasi Argon2 memakan waktu; tanpa langkah ini, nama yang tidak ada dijawab jauh lebih cepat daripada kata sandi yang salah, sehingga lama respons ikut membocorkan nama yang terdaftar (*timing attack*). Dokumentasi FastAPI memakai teknik yang sama.

### Endpoint debug

`/debug/hash/{nama}` hanya untuk percobaan, agar kamu bisa melihat bentuk hash. Di aplikasi nyata endpoint seperti ini tidak boleh ada.

## Menjalankan

```powershell
pip install "fastapi[standard]" "pwdlib[argon2]"
fastapi dev main.py
```

Tanda kutip diperlukan di PowerShell karena ada tanda kurung siku. Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah.

## Mencoba request

Hasil di bawah dijalankan dengan `curl.exe` (body dikirim dari berkas JSON dengan header `Content-Type: application/json`).

| Request | Status | Isi |
|---|---|---|
| `POST /daftar` `{"nama_pengguna":"budi","kata_sandi":"rahasia-saya-123"}` | `201` | `{"nama_pengguna":"budi"}` |
| `POST /daftar` (nama yang sama) | `409` | `{"detail":"Nama pengguna sudah dipakai"}` |
| `POST /daftar` `{"nama_pengguna":"bu","kata_sandi":"pendek"}` | `422` | dua error `string_too_short` (`nama_pengguna`, `kata_sandi`) |
| `POST /periksa-kata-sandi` (kata sandi benar) | `200` | `{"pesan":"Kata sandi cocok"}` |
| `POST /periksa-kata-sandi` (kata sandi salah) | `401` | `{"detail":"Nama pengguna atau kata sandi salah"}` |
| `POST /periksa-kata-sandi` (nama `hantu`) | `401` | `{"detail":"Nama pengguna atau kata sandi salah"}` |

Respons pendaftaran hanya berisi `nama_pengguna`. `/openapi.json` mencatat `PenggunaPublik` dengan satu properti, `nama_pengguna`.

### Bentuk hash tersimpan

`GET /debug/hash/budi`:

```json
{"hash":"$argon2id$v=19$m=65536,t=3,p=4$PkOdLyo4Vmu4v8KMrmZKeA$M94rRS/MBE+rtzUvVO2UMT+gqza6rK0A/yYRudoCGP8"}
```

Kata sandi `rahasia-saya-123` tidak terlihat di mana pun.

### Pengukuran waktu

Diuji dengan `TestClient`, rata-rata 8 percobaan dengan kata sandi yang salah:

| Kondisi | Rata-rata |
|---|---|
| Pengguna ada, kata sandi salah | 42 ms |
| Pengguna tidak ada | 43 ms |

Hampir sama, sehingga lama respons tidak membedakan keduanya. Angka bergantung pada mesin, dan satu pengukuran kecil seperti ini bukan bukti keamanan; ia hanya menunjukkan bahwa hash tiruan berfungsi seperti yang dimaksud.

### Dokumentasi otomatis

Tampilan visual Swagger UI **belum diverifikasi** lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Menyimpan kata sandi apa adanya | Kebocoran basis data membuka semua kata sandi. |
| Memakai enkripsi untuk kata sandi | Kunci yang bocor membuka semuanya. Pakai hashing satu arah. |
| Memakai hash cepat umum (SHA-256 biasa) | Terlalu mudah ditebak secara massal. Pakai algoritma kata sandi seperti Argon2. |
| Mengembalikan hash dalam response | Hash ikut bocor. Pakai skema output tanpa hash (teruji: `PenggunaPublik`). |
| Pesan error yang berbeda untuk "nama tidak ada" dan "kata sandi salah" | Penyerang bisa mengetahui nama pengguna yang terdaftar. |
| Tidak memakai hash tiruan untuk nama yang tidak ada | Waktu respons bisa membocorkan nama yang terdaftar. Pada pengujian, dengan hash tiruan waktunya hampir sama (42 ms dan 43 ms); tanpa hash tiruan tidak diukur di sini. |
| Meletakkan kata sandi di log | Kata sandi bisa terbaca dari log. Jangan dicatat. |
| Menaruh endpoint `/debug/hash` di aplikasi nyata | Membuka hash ke publik. Hanya untuk percobaan. |

## Latihan

1. **Dasar.** Mengapa dua hash dari kata sandi yang sama berbeda, dan mengapa verifikasi tetap berhasil?
2. **Prediksi.** Apa respons `POST /daftar` dengan `kata_sandi` sepanjang 7 karakter?
3. **Analisis.** Mengapa `/periksa-kata-sandi` menjawab pesan yang sama untuk nama yang tidak ada dan kata sandi yang salah?
4. **Praktik.** Tambahkan aturan: kata sandi tidak boleh sama dengan nama pengguna. Di mana kamu menaruhnya?

??? success "Kunci jawaban"
    Jawaban 2 mengacu pada hasil uji di atas. Jawaban 1, 3, dan 4 adalah penalaran dari kode dan penjelasan halaman ini; jawaban 4 tidak dijalankan.

    1. Salt acak ikut tertanam dalam hash (bagian setelah `p=4$`), sehingga hash berbeda setiap kali. Saat verifikasi, `pwdlib` membaca salt itu dari hash tersimpan dan menghitung ulang, jadi cocok.
    2. `422` dengan `string_too_short` pada `kata_sandi` (batas minimal 8), seperti contoh `pendek` di atas.
    3. Pesan berbeda membuat penyerang bisa tahu nama mana yang terdaftar. Pesan yang sama menyamarkannya.
    4. Pada `PenggunaBaru`, sebagai `model_validator` yang membandingkan dua field, atau pemeriksaan di endpoint `daftar` yang melempar `HTTPException(422)`. Pendekatan pertama tidak dibahas di Modul 03, jadi pemeriksaan di endpoint lebih mudah.

## Ringkasan

- Jangan simpan kata sandi apa adanya. Simpan **hash** satu arah.
- Gunakan algoritma khusus kata sandi (Argon2 lewat `pwdlib`), bukan hash cepat umum.
- Salt acak membuat hash dua kata sandi sama berbeda; verifikasi membaca salt dari hash.
- Endpoint pendaftaran tidak pernah mengembalikan kata sandi atau hash.
- Beri pesan error yang sama untuk nama tidak ada dan kata sandi salah, dan verifikasi terhadap hash tiruan agar waktu respons seragam.

## Langkah berikutnya

Lanjut ke [Token](token.md), atau kembali ke daftar materi di [Modul 07: Autentikasi dan Keamanan](index.md).
