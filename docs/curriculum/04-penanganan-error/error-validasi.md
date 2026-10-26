# Error Validasi

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan kapan FastAPI menjawab `422` dan mengapa fungsi endpoint tidak dijalankan.
- [ ] Membaca setiap bagian error: `type`, `loc`, `msg`, `input`, dan `ctx`.
- [ ] Menelusuri `loc` untuk menemukan asal data (`path`, `query`, `header`, `body`) dan field yang salah, termasuk di model bersarang dan `list`.
- [ ] Mengenali error karena JSON rusak, body hilang, atau `Content-Type` yang salah.
- [ ] Mengubah daftar error menjadi pesan per field di sisi klien.

## Prasyarat

- Sudah membaca [Status Code](status-code.md) dan [HTTPException](http-exception.md).
- Sudah membaca [Validasi Field](../03-data-validasi/validasi-field.md) dan [Validasi Path dan Query Parameter](../03-data-validasi/validasi-path-query.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, dan **Pydantic 2.14.1** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**. Pesan error (`msg`) berbahasa Inggris karena berasal dari Pydantic.

## Konsep

Di Modul 03 kamu sudah sering melihat response `422`. Halaman ini membahasnya sebagai topik tersendiri: bagaimana membacanya dengan teliti, dan bagaimana klien memakainya.

**Error validasi** terjadi ketika data request tidak sesuai deklarasi: tipe salah, aturan `Field`/`Query`/`Path` dilanggar, atau data wajib tidak ada. FastAPI memeriksa semuanya **sebelum** fungsi endpoint dijalankan. Bila ada yang gagal, jawabannya `422` dan fungsi tidak disentuh. Semua pelanggaran dikumpulkan dalam satu response, bukan satu per satu.

Bentuk responsnya selalu:

```json
{"detail": [ { "type": ..., "loc": [...], "msg": ..., "input": ..., "ctx": {...} }, ... ]}
```

| Kunci | Arti |
|---|---|
| `type` | Kode jenis error yang stabil, cocok dipakai program. Contoh: `missing`, `int_parsing`. |
| `loc` | Lokasi: asal data, lalu jalur ke field. Dibaca dari kiri ke kanan. |
| `msg` | Pesan manusiawi (bahasa Inggris). |
| `input` | Nilai yang ditolak. |
| `ctx` | Keterangan tambahan seperti batas yang dilanggar. Tidak selalu ada. |

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/04-penanganan-error/error-validasi/main.py"
```

Endpoint ini sengaja memakai semua sumber data: path (`kelas_id`), query (`sumber`), header (`x_versi`), dan body (model `Pendaftaran` dengan model bersarang `Alamat`). `Header` dipakai di sini hanya untuk membaca header request; ia berperan seperti `Query` untuk header.

## Penjelasan kode

- `Alamat` dan `Pendaftaran` adalah model Pydantic dengan aturan `Field`. `alamat` bersarang di dalam `Pendaftaran`.
- `kelas_id: Annotated[int, Path(ge=1)]` adalah path parameter dengan batas.
- `sumber` adalah query parameter dengan `min_length=2`.
- `x_versi: Annotated[int, Header(ge=1)] = 1` membaca header `x-versi`. FastAPI mengubah garis bawah pada nama variabel menjadi tanda hubung pada nama header (terlihat pada `loc` di bawah).
- Fungsi hanya mengembalikan data yang diterima. Bila fungsi ini berjalan, berarti semua validasi lolos.

## Menjalankan

```powershell
fastapi dev main.py
```

Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah.

## Mencoba request

Simpan body sebagai file JSON agar mudah dikirim dengan `curl.exe`.

### Request valid

```json title="valid.json"
{"nama":"Budi","umur":20,"alamat":{"kota":"Bandung","kode_pos":"40111"},"hobi":["baca"]}
```

```powershell
curl.exe -i -X POST http://127.0.0.1:8000/kelas/3/daftar -H "Content-Type: application/json" -d "@valid.json"
```

```text
HTTP/1.1 201 Created
{"kelas_id":3,"sumber":"web","x_versi":1,"data":{"nama":"Budi","umur":20,"alamat":{"kota":"Bandung","kode_pos":"40111"},"hobi":["baca"]}}
```

### Banyak kesalahan sekaligus

Body (`salah.json`): `{"nama":"Al","umur":12,"alamat":{"kota":"B","kode_pos":"abc"},"hobi":["a",1]}`. Request ini juga memakai `kelas_id` `0`, query `sumber=x`, dan header `x-versi: 0`:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/kelas/0/daftar?sumber=x" -H "Content-Type: application/json" -H "x-versi: 0" -d "@salah.json"
```

Hasilnya `422` dengan delapan error. Dirangkum dari response sebenarnya:

| # | `type` | `loc` | Penjelasan |
|---|---|---|---|
| 1 | `greater_than_equal` | `["path","kelas_id"]` | path parameter di bawah batas |
| 2 | `string_too_short` | `["query","sumber"]` | query terlalu pendek |
| 3 | `greater_than_equal` | `["header","x-versi"]` | header di bawah batas |
| 4 | `string_too_short` | `["body","nama"]` | field body |
| 5 | `greater_than_equal` | `["body","umur"]` | field body |
| 6 | `string_too_short` | `["body","alamat","kota"]` | field di model bersarang |
| 7 | `string_pattern_mismatch` | `["body","alamat","kode_pos"]` | pola tidak cocok |
| 8 | `string_type` | `["body","hobi",1]` | item ke-2 (indeks 1) dari `list` bukan teks |

Satu contoh lengkap, error nomor 7:

```json
{"type":"string_pattern_mismatch","loc":["body","alamat","kode_pos"],"msg":"String should match pattern '^\\d{5}$'","input":"abc","ctx":{"pattern":"^\\d{5}$"}}
```

#### Cara membaca `loc`

- **Elemen pertama** adalah asal data: `path`, `query`, `header`, atau `body`.
- **Elemen berikutnya** adalah jalur ke field. Nama kunci untuk objek, angka (mulai dari 0) untuk posisi dalam `list`.
- Untuk header, namanya memakai tanda hubung (`x-versi`), bukan garis bawah.

### Error pada bentuk request

Bukan hanya nilai; bentuk request juga bisa salah:

| Situasi | `type` | `loc` | Keterangan |
|---|---|---|---|
| Field bersarang wajib hilang (body tanpa `alamat`) | `missing` | `["body","alamat"]` | `input` berisi seluruh body yang diterima |
| Body kosong | `missing` | `["body"]` | `input` bernilai `null` |
| JSON rusak: `{"nama": "Budi", ` | `json_invalid` | `["body",17]` | angka 17 adalah posisi karakter; `ctx.error` berisi `Expecting property name enclosed in double quotes` |
| Tanpa header `Content-Type: application/json` | `model_attributes_type` | `["body"]` | `input` berisi teks mentah body. Dikirim apa adanya, body dianggap bukan objek JSON. |
| Header `x-versi: abc` | `int_parsing` | `["header","x-versi"]` | tipe salah |

Hasil uji dengan `TestClient`:

| Body | Hasil |
|---|---|
| `[]` (array, bukan objek) | `422` `model_attributes_type` di `["body"]` |
| `{"nama":"Budi","umur":"dua puluh","alamat":null}` | dua error: `int_parsing` di `["body","umur"]` dan `model_attributes_type` di `["body","alamat"]` |
| `"hobi":"baca"` (teks, bukan `list`) | `list_type` di `["body","hobi"]` |
| ada field tambahan `"extra":1` | `201`, field tambahan diabaikan |
| `kelas_id` berupa `abc` | `int_parsing` di `["path","kelas_id"]` |

### Membaca error di sisi klien

Daftar error bisa diolah program, misalnya untuk menandai kolom formulir yang salah. Simpan sebagai `baca_error.py`:

```python title="baca_error.py"
--8<-- "fastapi/04-penanganan-error/error-validasi/baca_error.py"
```

Skrip memakai `httpx`, yang terpasang bersama `fastapi[standard]`. Dengan server berjalan, jalankan `python baca_error.py`. Hasil sebenarnya (hanya alamat server yang disesuaikan dengan port uji):

```text
422
path:kelas_id -> Input should be greater than or equal to 1
query:sumber -> String should have at least 2 characters
body:nama -> String should have at least 3 characters
body:umur -> Input should be greater than or equal to 17
body:alamat.kode_pos -> String should match pattern '^\d{5}$'
```

Skrip ini mengirim data yang sedikit berbeda dari contoh sebelumnya: `kota` bernilai `"Bandung"` (valid) dan `hobi` tidak dikirim, sehingga hanya lima error yang muncul. Kunci `dict` berbentuk `asal:jalur`, misalnya `body:alamat.kode_pos`.

!!! note "Catatan"
    Bila dua error memiliki `loc` yang sama, `dict` hanya menyimpan yang terakhir. Untuk kebutuhan nyata, simpan daftar pesan per kunci.

### Dokumentasi otomatis

Aturan validasi yang dideklarasikan tampil di `/openapi.json` dan `/docs`. Tampilan visual di Swagger UI **belum diverifikasi** lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Menganggap `422` adalah kesalahan server | `422` adalah `4xx`: kesalahan ada di request klien. Kesalahan server memakai `5xx`. |
| Mencari error di dalam fungsi endpoint | Fungsi tidak dijalankan saat validasi gagal. Lihat `loc` dan `type`. |
| Membaca `loc` seolah selalu berupa `["body", "nama"]` | Elemen pertama bisa `path`, `query`, `header`, atau `body`; elemen berikutnya bisa angka (posisi di `list`). |
| Menampilkan `msg` bahasa Inggris langsung ke pengguna akhir | `msg` berasal dari Pydantic. Pakai `type` untuk memilih pesan sendiri. |
| Memperbaiki satu error lalu kirim ulang berkali-kali | Semua pelanggaran sudah dilaporkan sekaligus. Perbaiki semuanya dari satu response. |
| Mengirim JSON tanpa `Content-Type: application/json` | Teruji: `422` dengan `model_attributes_type`. Body dianggap teks. |

## Latihan

1. **Baca.** Dari tabel "Banyak kesalahan sekaligus", error mana yang menunjuk ke field di dalam model bersarang? Tulis `loc`-nya.
2. **Prediksi.** Apa `type` dan `loc` untuk body `{"nama":"Budi","umur":20}` pada `POST /kelas/1/daftar`?
3. **Prediksi 2.** Apa yang terjadi bila `hobi` dikirim sebagai `"baca"` (teks, bukan `list`)? Dan bila ada field tambahan `"extra": 1`?
4. **Analisis.** Mengapa error JSON rusak memiliki `loc` `["body", 17]`, bukan nama field?

??? success "Kunci jawaban"
    1. Error nomor 6 dan 7: `["body","alamat","kota"]` dan `["body","alamat","kode_pos"]`.
    2. `missing` dengan `loc` `["body","alamat"]`. Teruji.
    3. `"hobi":"baca"` menghasilkan `list_type` di `["body","hobi"]`. Field tambahan `"extra":1` diabaikan (status `201`). Teruji dengan `TestClient`.
    4. JSON yang rusak tidak bisa diurai sama sekali, jadi FastAPI belum tahu field mana pun. Angka 17 menunjukkan posisi di teks tempat kerusakan ditemukan (menurut hasil uji pada body contoh, bukan hasil penelusuran sumber FastAPI).

## Ringkasan

- `422` berarti request tidak lolos validasi; fungsi endpoint tidak dijalankan.
- Semua pelanggaran dilaporkan sekaligus dalam `detail`, berupa daftar objek.
- `type` untuk program, `msg` untuk manusia (bahasa Inggris), `input` nilai yang ditolak, `ctx` keterangan tambahan.
- `loc` dibaca dari kiri: asal data (`path`, `query`, `header`, `body`), lalu jalur field, lalu indeks `list` bila ada.
- Bentuk request yang rusak (JSON tidak valid, body kosong, `Content-Type` salah) juga menghasilkan `422`.
- Klien dapat memetakan `loc` ke kolom formulir untuk menampilkan pesan per field.

## Langkah berikutnya

Kembali ke daftar materi di [Modul 04: Penanganan Error](index.md). Materi berikutnya adalah handler error kustom: mengubah bentuk response `422` dan error lain agar seragam.
