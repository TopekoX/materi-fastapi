# Otorisasi

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Membedakan **autentikasi** ("kamu siapa?") dari **otorisasi** ("kamu boleh apa?").
- [ ] Membatasi endpoint berdasarkan **peran** dengan dependency pabrik `wajib_peran`.
- [ ] Membatasi akses berdasarkan **kepemilikan data**.
- [ ] Memilih antara `401`, `403`, dan `404` dengan alasan yang jelas.
- [ ] Menjaga agar hasil daftar hanya memuat data yang boleh dilihat pemanggil.
- [ ] Mengenali scope sebagai izin per token dan memeriksanya dengan `Security` dan `SecurityScopes`.

## Prasyarat

- Sudah membaca [Proteksi Endpoint](proteksi-endpoint.md).
- Sudah membaca [Dependency Berantai](../05-dependency-injection/dependency-berantai.md) dan [Status Code](../04-penanganan-error/status-code.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **PyJWT 2.15.1**, dan **pwdlib 0.3.1** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

| | Autentikasi | Otorisasi |
|---|---|---|
| Pertanyaan | Kamu siapa? | Kamu boleh melakukan ini? |
| Dibuktikan dengan | Kata sandi, token | Aturan: peran, kepemilikan |
| Gagal berarti | `401` | `403` |
| Dibahas | [Token](token.md), [Proteksi Endpoint](proteksi-endpoint.md) | halaman ini |

Pengguna yang berhasil login belum tentu boleh melakukan semuanya. Halaman ini membahas dua aturan yang paling umum:

1. **Berdasarkan peran** (*role*): sebagian endpoint hanya untuk peran tertentu, misalnya `pengelola`.
2. **Berdasarkan kepemilikan**: pengguna boleh mengubah data miliknya sendiri, tetapi tidak milik orang lain (kecuali `pengelola`).

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/07-autentikasi-keamanan/otorisasi/main.py"
```

Bagian autentikasi (`/token` dan `pengguna_saat_ini`) sama dengan halaman sebelumnya, ditambah data peran pada pengguna. Tiga pengguna contoh dibuat saat aplikasi mulai: `budi` dan `sari` berperan `anggota`, `rina` berperan `pengelola`. Kata sandi demo ditulis di kode **hanya untuk percobaan**.

## Penjelasan kode

### Peran pada pengguna

```python
pengguna_db = {
    "budi": {"hash": ..., "peran": "anggota"},
    "sari": {"hash": ..., "peran": "anggota"},
    "rina": {"hash": ..., "peran": "pengelola"},
}
```

`pengguna_saat_ini` kini mengembalikan model `Pengguna` yang memuat `peran`. Peran itu diambil dari data pengguna, **bukan dari token**, sehingga mengubah peran pengguna langsung berlaku tanpa menunggu token lama kedaluwarsa. (Pilihan perancangan: menaruh peran di token juga mungkin, tetapi tidak dibahas di sini.)

### Otorisasi peran: `wajib_peran`

```python
def wajib_peran(*peran_diizinkan: str):
    def periksa(pengguna: PenggunaLogin) -> Pengguna:
        if pengguna.peran not in peran_diizinkan:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Hanya untuk peran: {', '.join(peran_diizinkan)}",
            )
        return pengguna

    return periksa
```

`wajib_peran` adalah **fungsi yang menghasilkan dependency**. `wajib_peran("pengelola")` mengembalikan fungsi `periksa` yang sudah "mengingat" peran yang diizinkan. Dengan begitu satu fungsi bisa membuat banyak aturan: `wajib_peran("pengelola")`, atau `wajib_peran("anggota", "pengelola")`.

`periksa` bergantung pada `PenggunaLogin`, sehingga rantai autentikasi ikut berjalan lebih dulu. Dipakai seperti ini:

```python
@app.get("/laporan")
def laporan(pengelola: Annotated[Pengguna, Depends(wajib_peran("pengelola"))]):
```

### Otorisasi kepemilikan

```python
def tugas_yang_boleh_diubah(tugas_id: int, pengguna: PenggunaLogin) -> dict:
    tugas = tugas_db.get(tugas_id)
    if tugas is None:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")
    if tugas["pemilik"] != pengguna.nama_pengguna and pengguna.peran != "pengelola":
        raise HTTPException(status_code=403, detail="Tugas ini bukan milikmu")
    return tugas
```

Dependency ini mengambil tugas dan memeriksa tiga hal berurutan: tugas ada (`404`), pemanggil adalah pemiliknya atau pengelola (`403`), baru mengembalikan tugasnya. `PUT` dan `DELETE` memakainya, sehingga aturan kepemilikan ditulis sekali.

### Daftar yang disaring

```python
@app.get("/tugas")
def daftar_tugas_saya(pengguna: PenggunaLogin):
    if pengguna.peran == "pengelola":
        return list(tugas_db.values())
    return [t for t in tugas_db.values() if t["pemilik"] == pengguna.nama_pengguna]
```

Otorisasi pada daftar berarti **menyaring** isinya: anggota hanya menerima tugasnya, bukan menolak seluruh request. Endpoint pembuatan (`POST /tugas`) mengisi `pemilik` dari pengguna yang login, bukan dari body, supaya klien tidak bisa membuat tugas atas nama orang lain.

## Menjalankan

```powershell
$env:SECRET_KEY = "isi-dengan-kunci-acak-hasil-perintah-di-halaman-token"
fastapi dev main.py
```

Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah.

## Mencoba request

Hasil di bawah dijalankan dengan `curl.exe`. Login lewat `POST /token` (formulir `username` dan `password`) untuk mendapat token `budi`, `sari`, dan `rina`.

### Berdasarkan peran: `GET /laporan`

| Pemanggil | Status | Isi |
|---|---|---|
| tanpa token | `401` | `{"detail":"Not authenticated"}` |
| `budi` (anggota) | `403` | `{"detail":"Hanya untuk peran: pengelola"}` |
| `rina` (pengelola) | `200` | `{"pesan":"Laporan untuk rina","jumlah_tugas":2}` |

Perhatikan perbedaannya: tanpa token adalah `401` (belum terbukti siapa), sedangkan `budi` mendapat `403` (terbukti siapa, tetapi tidak diizinkan).

### Daftar yang disaring: `GET /tugas`

| Pemanggil | Isi |
|---|---|
| `budi` | hanya tugas 1 (`Tugas milik Budi`) |
| `sari` | hanya tugas 2 (`Tugas milik Sari`) |
| `rina` (pengelola) | kedua tugas |

### Berdasarkan kepemilikan

| Request | Status | Isi |
|---|---|---|
| `budi` `POST /tugas` `{"judul":"Tugas baru Budi"}` | `201` | `{"id":3,"judul":"Tugas baru Budi","pemilik":"budi"}` |
| `budi` `PUT /tugas/1` (miliknya) | `200` | `{"id":1,"judul":"Diganti","pemilik":"budi"}` |
| `budi` `PUT /tugas/2` (milik sari) | `403` | `{"detail":"Tugas ini bukan milikmu"}` |
| `budi` `DELETE /tugas/2` | `403` | pesan yang sama |
| `rina` `DELETE /tugas/2` | `204` | tanpa isi (pengelola boleh) |
| `budi` `PUT /tugas/99` | `404` | `{"detail":"Tugas tidak ditemukan"}` |
| `budi` `DELETE /tugas/1` | `204` | tanpa isi |

Akhirnya `GET /tugas` oleh `rina` hanya menampilkan tugas 3, yang sisa.

### `403` atau `404` untuk data milik orang lain?

Contoh ini menjawab `403` untuk tugas milik orang lain, sehingga `budi` tahu bahwa tugas 2 **ada**. Pada sebagian aplikasi, keberadaan data tidak boleh bocor; mereka menjawab `404` untuk data yang tidak boleh dilihat. Pilihan perancangan itu tidak diuji di sini.

### Dokumentasi otomatis

`/openapi.json` mencatat skema `OAuth2PasswordBearer` untuk endpoint terlindungi, seperti di halaman sebelumnya. Tampilan Swagger UI **belum diverifikasi** lewat browser.

## Scope (izin per token)

Selain peran, OAuth2 mengenal **scope**: nama izin berupa teks yang dicantumkan di dalam token, misalnya `tugas:baca` dan `tugas:tulis`. Beda dengan peran yang melekat pada pengguna, scope melekat pada **token**, sehingga satu pengguna bisa memegang token dengan izin berbeda-beda (misalnya token hanya-baca untuk aplikasi pihak ketiga).

Menurut dokumentasi FastAPI, scope hanyalah teks. FastAPI tidak menegakkannya sendiri: ia menyediakan `Security` dan `SecurityScopes` untuk memeriksanya, dan kodemulah yang menolak bila izin kurang. Dokumentasi juga menyebut scope sebagai fitur yang lebih lanjut dan bersifat opsional. Bagian ini hanya perkenalan singkat; contoh lengkap ada di `main_scopes.py`:

```python title="main_scopes.py"
--8<-- "fastapi/07-autentikasi-keamanan/otorisasi/main_scopes.py"
```

### Bagian pentingnya

- `OAuth2PasswordBearer(tokenUrl="token", scopes={...})` mendeklarasikan scope beserta deskripsinya untuk dokumentasi otomatis.
- Saat login, klien meminta scope lewat kolom `scope` formulir (dipisahkan spasi). Server **hanya memasukkan scope yang diminta dan diizinkan** untuk pengguna itu (`scope_boleh`): `diberikan = [s for s in form.scopes if s in pengguna["scope_boleh"]]`. Dokumentasi FastAPI mengingatkan bahwa hanya scope yang memang boleh dimiliki pengguna yang boleh masuk token; menyalin permintaan klien begitu saja berbahaya.
- Scope disimpan di token sebagai klaim `scope` berupa teks yang dipisahkan spasi.
- `Security(pengguna_dengan_scope, scopes=["tugas:tulis"])` adalah `Depends` yang juga membawa daftar scope yang dibutuhkan. Dependency menerimanya lewat parameter `SecurityScopes`, lalu membandingkannya dengan scope di token.

### Hasil uji

Dengan `curl.exe`, pengguna `budi` boleh `tugas:baca` dan `tugas:tulis`, sedangkan `tamu` hanya `tugas:baca`. Kolom `scope` pada login adalah `tugas:baca tugas:tulis`:

| Login | Scope di token |
|---|---|
| `budi` meminta dua scope | `tugas:baca tugas:tulis` |
| `tamu` meminta dua scope | `tugas:baca` (permintaan `tugas:tulis` diabaikan server) |
| `budi` tanpa meminta scope | kosong |

| Request | Status | Isi |
|---|---|---|
| `GET /tugas`, token `budi` | `200` | `{"untuk":"budi","tugas":["Belajar scope"]}` |
| `POST /tugas`, token `budi` | `201` | `{"dibuat_oleh":"budi"}` |
| `GET /tugas`, token `tamu` | `200` | `{"untuk":"tamu",...}` |
| `POST /tugas`, token `tamu` | `403` | `{"detail":"Butuh scope: tugas:tulis"}`, header `www-authenticate: Bearer scope="tugas:tulis"` |
| `POST /tugas`, token `budi` yang hanya `tugas:baca` | `403` | pesan dan header yang sama |
| `GET /tugas`, token tanpa scope | `403` | `Butuh scope: tugas:baca` |
| `GET /tugas` tanpa token | `401` | `{"detail":"Not authenticated"}` |

`/openapi.json` mencatat deskripsi scope pada skema `OAuth2PasswordBearer`, dan menandai `GET /tugas` dengan `tugas:baca` serta `POST /tugas` dengan `tugas:tulis`. Dialog *Authorize* di `/docs` **belum diverifikasi** lewat browser.

!!! note "Perbedaan kecil dengan dokumentasi FastAPI"
    Contoh di dokumentasi FastAPI menjawab `401` dengan `Not enough permissions` untuk scope yang kurang. Halaman ini menjawab `403`, selaras dengan pembedaan `401` (identitas) dan `403` (izin) di atas. Keduanya pilihan perancangan; yang penting konsisten.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Menjawab `401` untuk pengguna yang tidak diizinkan | Klien mengira harus login ulang. Pakai `403`. |
| Hanya menyembunyikan tombol di antarmuka tanpa memeriksa di server | Siapa pun bisa memanggil API langsung. Selalu periksa di server. |
| Mengambil `pemilik` dari body request | Klien bisa membuat data atas nama orang lain. Ambil dari pengguna yang login. |
| Mengembalikan semua data lalu berharap klien menyaring | Data orang lain bocor. Saring di server (teruji: `GET /tugas`). |
| Mengulang pemeriksaan peran di setiap endpoint | Mudah terlewat. Pakai dependency seperti `wajib_peran`. |
| Memeriksa kepemilikan hanya di `PUT` dan lupa `DELETE` | Data bisa dihapus orang lain. Pada contoh, dependency yang sama dipakai keduanya. |
| Menyimpan peran di data yang bisa diubah klien | Klien bisa menaikkan hak sendiri. Peran hanya diubah oleh sisi server. |

## Latihan

1. **Dasar.** Mengapa `budi` mendapat `403` pada `/laporan`, sedangkan permintaan tanpa token mendapat `401`?
2. **Praktik.** Tambahkan `GET /tugas/{tugas_id}` yang bisa dibaca pemilik atau pengelola, memakai dependency yang sudah ada.
3. **Prediksi.** Apa status `rina` `PUT /tugas/2` dengan body valid? Mengapa?
4. **Analisis.** Mengapa `pemilik` diisi dari pengguna yang login, bukan dari body?

??? success "Kunci jawaban"
    Jawaban 1 dan 3 mengacu pada hasil uji di atas. Jawaban 2 adalah penerapan pola yang teruji pada `PUT` dan `DELETE`, tidak dijalankan. Jawaban 4 adalah penalaran.

    1. `401` berarti identitas belum terbukti (tidak ada token). `403` berarti identitas terbukti, tetapi peran `anggota` tidak diizinkan.
    2. ```python
       @app.get("/tugas/{tugas_id}")
       def baca_tugas(tugas: Annotated[dict, Depends(tugas_yang_boleh_diubah)]):
           return tugas
       ```
       Nama dependency menyebut "diubah"; untuk kebutuhan nyata, ganti namanya menjadi lebih umum, misalnya `tugas_yang_boleh_diakses`.
    3. `200`. Pengelola lolos pemeriksaan kepemilikan karena `pengguna.peran == "pengelola"`. (Pola ini teruji pada `DELETE` oleh `rina`, yang menghasilkan `204`.)
    4. Agar klien tidak bisa membuat atau memindahkan data atas nama orang lain; sumber kebenaran identitas adalah token yang sudah diverifikasi server.

## Ringkasan

- Autentikasi menjawab "kamu siapa" (`401`), otorisasi menjawab "kamu boleh apa" (`403`).
- Otorisasi peran dibuat dengan dependency pabrik `wajib_peran(...)`.
- Otorisasi kepemilikan memeriksa pemilik data, dengan pengecualian untuk peran tertentu.
- Daftar disaring di server sesuai hak pemanggil.
- `pemilik` diambil dari pengguna yang login, bukan dari body.
- Pemeriksaan harus ada di server, bukan hanya di antarmuka.
- Scope adalah izin per token berupa teks; server hanya memasukkan scope yang diminta dan diizinkan, dan kode yang memeriksanya.

## Langkah berikutnya

Lanjut ke [CORS](cors.md), atau kembali ke daftar materi di [Modul 07: Autentikasi dan Keamanan](index.md).
