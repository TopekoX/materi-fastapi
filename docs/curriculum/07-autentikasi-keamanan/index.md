# Modul 07: Autentikasi dan Keamanan

**Tingkat:** Menengah–Lanjut

## Tujuan pembelajaran

Setelah modul ini, kamu mampu:

- [ ] Menyimpan password dengan aman memakai hashing.
- [ ] Menerapkan login berbasis token.
- [ ] Melindungi endpoint agar hanya dapat diakses pengguna terautentikasi.
- [ ] Membedakan autentikasi dan otorisasi, lalu menerapkan otorisasi dasar.
- [ ] Memahami dan mengatur CORS.
- [ ] Menyelesaikan tahap 4 proyek praktik: registrasi, login, dan endpoint terlindungi.

## Prasyarat

- [Modul 06: Basis Data](../06-basis-data/index.md)
- Pemahaman dependency dari [Modul 05](../05-dependency-injection/index.md).

## Daftar materi

- [Hashing password](hashing-password.md)
- [Token](token.md)
- [Proteksi endpoint](proteksi-endpoint.md)
- [Refresh token dan pencabutan](refresh-token.md)
- [Otorisasi](otorisasi.md)
- [CORS](cors.md)
- [Proyek praktik tahap 4](proyek-tahap-4.md)

!!! info "Status"
    Semua materi Modul 07 sudah tersedia. Modul ini memakai pwdlib (Argon2) untuk hashing, PyJWT untuk token, dan `OAuth2PasswordBearer` untuk proteksi endpoint.
