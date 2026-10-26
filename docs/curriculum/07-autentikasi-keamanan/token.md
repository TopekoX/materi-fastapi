# Token

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan mengapa API memakai token, bukan mengirim kata sandi di setiap request.
- [ ] Menjelaskan struktur JWT: header, payload, dan tanda tangan.
- [ ] Menjelaskan bahwa JWT ditandatangani, bukan dienkripsi.
- [ ] Membuat dan memverifikasi token dengan PyJWT, termasuk masa berlaku (`exp`) dan klaim `sub`.
- [ ] Membuat endpoint login `/token` yang menerima data formulir.
- [ ] Membaca kunci penandatangan dari variabel environment.

## Prasyarat

- Sudah membaca [Hashing Password](hashing-password.md).
- Sudah membaca [Status Code](../04-penanganan-error/status-code.md) dan [HTTPException](../04-penanganan-error/http-exception.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **PyJWT 2.15.1**, **pwdlib 0.3.1**, dan **python-multipart 0.0.32** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

### Masalah: kata sandi di setiap request

HTTP tidak mengingat siapa kamu antar request. Kalau API harus menerima kata sandi di setiap request, kata sandi akan sering melintas di jaringan, dan setiap kali server harus menjalankan hashing yang sengaja lambat. Solusinya adalah **token**: setelah login sekali, klien menerima sebuah bukti yang bisa dikirim pada request berikutnya.

```mermaid
sequenceDiagram
    participant K as Klien
    participant S as Server
    K->>S: POST /token (nama pengguna dan kata sandi)
    S-->>K: access_token
    K->>S: request berikutnya (Authorization: Bearer token)
    S-->>K: data
```

Cara memakai token pada request berikutnya dibahas di [Proteksi Endpoint](proteksi-endpoint.md). Halaman ini fokus pada **membuat dan memverifikasi** token.

### JWT

**JWT** (*JSON Web Token*) adalah format token yang umum dipakai. Satu token terdiri dari tiga bagian yang dipisahkan titik:

```text
header . payload . tanda_tangan
```

| Bagian | Isi |
|---|---|
| **Header** | Jenis token dan algoritma penandatanganan (di contoh: `HS256`) |
| **Payload** | Data yang dibawa token, disebut *claims*, misalnya `sub` dan `exp` |
| **Tanda tangan** | Hasil menandatangani header dan payload dengan **kunci rahasia** milik server |

Dua klaim yang kita pakai:

- `sub` (*subject*): siapa pemilik token. Menurut dokumentasi FastAPI, ini tempat standar menyimpan pengenal pengguna, dan nilainya sebaiknya unik di seluruh aplikasi.
- `exp` (*expiration*): kapan token berhenti berlaku.

!!! warning "Ditandatangani, bukan dienkripsi"
    Siapa pun yang memegang token bisa **membaca** isinya (payload hanya dikodekan, bukan disembunyikan). Tanda tangan hanya menjamin isinya **tidak diubah**. Karena itu jangan menaruh kata sandi atau data rahasia di payload.

### Kunci penandatangan

Server menandatangani dengan **kunci rahasia**. Siapa pun yang memiliki kunci itu bisa membuat token palsu yang tampak sah, sehingga kunci:

- harus acak dan panjang,
- **tidak boleh ditulis di kode** atau dikirim ke Git,
- dibaca dari variabel environment.

Membuat kunci:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Mengisinya di PowerShell untuk sesi terminal saat ini (ganti dengan kunci hasil perintah di atas):

```powershell
$env:SECRET_KEY = "isi-dengan-kunci-acak-hasil-perintah-di-atas"
```

Pengelolaan konfigurasi lebih lanjut, termasuk berkas `.env`, dibahas di [Modul 08](../08-struktur-proyek/index.md) dan [Modul 10](../10-deployment/index.md). Pengiriman token lewat HTTPS juga bagian dari deployment (Modul 10); contoh di modul ini berjalan lewat HTTP biasa di komputer lokal, yang tidak aman untuk aplikasi nyata.

Setelah memahami cara kerja token di halaman ini, [Refresh Token dan Pencabutan](refresh-token.md) membahas cara memperbarui dan mencabutnya.

### Pemasangan

```powershell
pip install "fastapi[standard]" pyjwt "pwdlib[argon2]"
```

`fastapi[standard]` menyertakan `python-multipart` (teruji: terpasang bersama FastAPI di venv uji), yang dibutuhkan untuk membaca data formulir login.

## Mencoba dasarnya

Simpan sebagai `dasar_jwt.py`:

```python title="dasar_jwt.py"
--8<-- "fastapi/07-autentikasi-keamanan/token/dasar_jwt.py"
```

Jalankan `python dasar_jwt.py`. Hasil sebenarnya (nilai token dan `exp` berbeda setiap kali):

```text
token  : eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJidWRpIiwiZXhwIjoxNzkzMDE4NTMxfQ.UrqCt5RfPSnM4cHWFjz6SwOjPWPCHxPSg4NM8DGck1o
bagian : 3
header : {'alg': 'HS256', 'typ': 'JWT'}
payload: {'sub': 'budi', 'exp': 1793018531}
valid  : budi
diubah : InvalidSignatureError - Signature verification failed
kunci salah: InvalidSignatureError
kedaluwarsa: ExpiredSignatureError - Signature has expired
sembarang  : DecodeError - Not enough segments
```

### Penjelasan

- `jwt.encode(isi, KUNCI, algorithm=...)` membuat token. `exp` diberikan sebagai waktu UTC.
- Token punya **tiga bagian**. Header dan payload bisa dibaca siapa saja setelah di-*decode* dari base64 (skrip melakukannya dengan `baca_base64`). Perhatikan `sub` dan `exp` terlihat jelas.
- `jwt.decode(token, KUNCI, algorithms=[...])` memverifikasi tanda tangan dan masa berlaku, lalu mengembalikan payload. Daftar `algorithms` wajib diisi eksplisit.
- Token yang **isinya diubah** (di sini `sub` dari `budi` menjadi `admin`) gagal dengan `InvalidSignatureError`, karena tanda tangan tidak lagi cocok.
- **Kunci yang salah** juga gagal dengan `InvalidSignatureError`.
- Token **kedaluwarsa** gagal dengan `ExpiredSignatureError`.
- Teks sembarang gagal dengan `DecodeError`.
- Ketiga kelas galat tadi adalah turunan `InvalidTokenError`, sehingga satu `except InvalidTokenError` menangkap semuanya.

## Kode lengkap

Aplikasi FastAPI-nya. Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/07-autentikasi-keamanan/token/main.py"
```

## Penjelasan kode

### Kunci dari environment

```python
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("Variabel environment SECRET_KEY belum diisi. ...")
```

Aplikasi menolak mulai bila kunci tidak ada. Hasil uji tanpa `SECRET_KEY`:

```text
RuntimeError: Variabel environment SECRET_KEY belum diisi. Buat kunci dengan: python -c "import secrets; print(secrets.token_hex(32))"
```

Lebih baik gagal jelas daripada diam-diam memakai kunci bawaan yang diketahui semua orang.

### Membuat token

```python
def buat_token(nama_pengguna: str, berlaku: timedelta) -> str:
    isi = {"sub": nama_pengguna, "exp": datetime.now(timezone.utc) + berlaku}
    return jwt.encode(isi, SECRET_KEY, algorithm=ALGORITMA)
```

`sub` diisi nama pengguna, dan `exp` diisi sekarang ditambah masa berlaku (30 menit). Masa berlaku pendek membatasi kerusakan bila token bocor.

### Autentikasi

```python
def autentikasi(nama_pengguna: str, kata_sandi: str) -> bool:
    hash_tersimpan = pengguna_db.get(nama_pengguna)
    if hash_tersimpan is None:
        password_hash.verify(kata_sandi, HASH_TIRUAN)
        return False
    return password_hash.verify(kata_sandi, hash_tersimpan)
```

Logika yang sama dengan [Hashing Password](hashing-password.md), termasuk hash tiruan agar waktu respons seragam.

### Endpoint login

```python
@app.post("/token")
def masuk(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
```

- `OAuth2PasswordRequestForm` membaca `username` dan `password` dari **data formulir** (`application/x-www-form-urlencoded`), bukan JSON. Ini tata cara OAuth2 yang dipakai FastAPI, dan membuat tombol *Authorize* di `/docs` bekerja.
- Bila gagal, jawabannya `401` dengan header `WWW-Authenticate: Bearer`, sesuai konvensi `401` pada HTTP.
- Bila berhasil, klien menerima `access_token` dan `token_type` (`bearer`).

`/periksa-token` hanya endpoint percobaan untuk melihat hasil verifikasi. Perlindungan endpoint yang sebenarnya dibahas di halaman berikutnya.

## Menjalankan

```powershell
$env:SECRET_KEY = "isi-dengan-kunci-acak-hasil-perintah-di-atas"
fastapi dev main.py
```

Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah.

## Mencoba request

Hasil di bawah dijalankan dengan `curl.exe`. Daftarkan `budi` dengan body JSON `{"nama_pengguna":"budi","kata_sandi":"rahasia-saya-123"}` (`201`), lalu login. Data login dikirim sebagai **formulir**, bukan JSON:

```powershell
curl.exe -i -X POST http://127.0.0.1:8000/token -d "username=budi&password=rahasia-saya-123"
```

```text
HTTP/1.1 200 OK
{"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJidWRpIiwiZXhwIjoxNzkzMDE4NTU4fQ.zG6BuHgmK4X9Vnx746g2DYpTzKGnq7nn7bqapfEAatU","token_type":"bearer"}
```

| Request | Status | Isi |
|---|---|---|
| `/token`, kata sandi salah | `401` | `{"detail":"Nama pengguna atau kata sandi salah"}`, header `www-authenticate: Bearer` |
| `/token`, nama `hantu` | `401` | pesan dan header yang sama |
| `/token` tanpa data | `422` | dua error `missing` pada `["body","username"]` dan `["body","password"]` |
| `/token` dengan body JSON | `422` | error yang sama: JSON tidak dibaca sebagai formulir |
| `GET /periksa-token?token=<token valid>` | `200` | `{"sub":"budi","exp":1793018559}` |
| `GET /periksa-token?token=<token + "x">` | `401` | `{"detail":"Token tidak valid: InvalidSignatureError"}` |
| `GET /periksa-token?token=bukan-token` | `401` | `{"detail":"Token tidak valid: DecodeError"}` |

Token berpanjang 123 karakter pada percobaan ini. `/openapi.json` dan tombol *Authorize* di `/docs` belum diperiksa lewat browser; tampilan visual Swagger UI **belum diverifikasi**.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Menulis `SECRET_KEY` langsung di kode | Kunci ikut ke Git dan bisa dipakai siapa pun untuk membuat token palsu. |
| Memakai kunci pendek atau mudah ditebak | Token bisa dipalsukan dengan menebak kunci. Pakai kunci acak panjang. |
| Menaruh data rahasia di payload | Payload bisa dibaca siapa saja (teruji lewat `baca_base64`). |
| Token tanpa `exp` | Token berlaku selamanya. Selalu beri masa berlaku. |
| Tidak mengisi `algorithms` saat `decode` | PyJWT mewajibkannya; jangan menerima algoritma sembarang. |
| Mengirim data login sebagai JSON ke `/token` | `422` (teruji). Kirim sebagai formulir. |
| Menangkap `Exception` terlalu luas | Menyembunyikan bug lain. Tangkap `InvalidTokenError`. |
| Menganggap token bisa dicabut seketika | Token JWT tetap sah sampai `exp` selama kunci tidak berubah. Pencabutan tidak dibahas di sini. |

## Latihan

1. **Dasar.** Sebutkan tiga bagian JWT dan jelaskan apa yang dijamin oleh tanda tangan.
2. **Prediksi.** Apa yang terjadi bila seseorang mengubah `sub` di payload dari `budi` menjadi `admin`?
3. **Praktik.** Ubah `MENIT_KEDALUWARSA` menjadi sangat singkat dan jelaskan bagaimana kamu membuktikan token kedaluwarsa.
4. **Analisis.** Mengapa `/token` menjawab pesan yang sama untuk nama yang tidak ada dan kata sandi yang salah?

??? success "Kunci jawaban"
    Jawaban 2 mengacu pada hasil `dasar_jwt.py`. Jawaban 3 mengacu pada perilaku `ExpiredSignatureError` di skrip yang sama. Jawaban 1 dan 4 adalah penalaran.

    1. Header, payload, dan tanda tangan. Tanda tangan menjamin isi header dan payload tidak diubah sejak ditandatangani server dengan kunci rahasia. Ia tidak menyembunyikan isi.
    2. Verifikasi gagal dengan `InvalidSignatureError` ("Signature verification failed"), karena tanda tangan lama tidak cocok dengan payload baru.
    3. Buat token dengan masa berlaku singkat (misalnya `timedelta(seconds=1)`), tunggu lebih dari itu, lalu panggil `/periksa-token`. Seharusnya terjadi `ExpiredSignatureError`. `dasar_jwt.py` membuktikannya dengan token yang `exp`-nya sudah lewat. Pada `/periksa-token`, kegagalan ini tampil sebagai `401` dengan teks `Token tidak valid: ExpiredSignatureError` (tidak dijalankan lewat endpoint).
    4. Agar penyerang tidak bisa menebak nama pengguna yang terdaftar.

## Ringkasan

- Token membuat klien cukup login sekali; request berikutnya membawa token.
- JWT = header + payload + tanda tangan. Ditandatangani, **bukan** dienkripsi.
- `sub` menyimpan pemilik token, `exp` masa berlakunya.
- `jwt.encode` membuat token, `jwt.decode` memverifikasi tanda tangan dan masa berlaku. Perubahan isi, kunci salah, dan kedaluwarsa semuanya gagal.
- Kunci penandatangan dibaca dari variabel environment dan tidak boleh ada di kode.
- Endpoint login `/token` menerima data formulir lewat `OAuth2PasswordRequestForm` dan mengembalikan `access_token`.

## Langkah berikutnya

Lanjut ke [Proteksi Endpoint](proteksi-endpoint.md), atau kembali ke daftar materi di [Modul 07: Autentikasi dan Keamanan](index.md).
