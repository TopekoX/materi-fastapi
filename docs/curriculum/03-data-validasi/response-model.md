# Response Model

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan apa itu response model dan mengapa data keluar perlu difilter.
- [ ] Memisahkan model input dan model output agar data sensitif (misalnya kata sandi) tidak bocor.
- [ ] Memasang `response_model` pada dekorator, termasuk untuk `list`.
- [ ] Memakai pewarisan model dan anotasi tipe kembalian sebagai alternatif.
- [ ] Mengatur isi response dengan `response_model_exclude_unset` dan `response_model_exclude`.
- [ ] Mengenali error `500` akibat data keluar yang tidak sesuai model.

## Prasyarat

- Sudah membaca [Model Pydantic](model-pydantic.md) dan [Request Body](request-body.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, dan **Pydantic 2.14.1** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Sampai sekarang model Pydantic dipakai untuk memeriksa data **masuk**. Model juga bisa dipakai untuk data **keluar**. Itulah **response model**: bentuk data yang dijanjikan endpoint kepada pemanggilnya.

Menurut dokumentasi FastAPI, response model dipakai untuk:

- **memvalidasi** data yang dikembalikan,
- **memfilter** data, sehingga field di luar model tidak ikut terkirim,
- menyusun skema di dokumentasi otomatis.

Alasan utama pemfilteran adalah keamanan. Bayangkan endpoint pendaftaran akun. Data masuk berisi `kata_sandi`, tetapi data keluar tidak boleh memuatnya. Bila endpoint mengembalikan model yang sama dengan inputnya, kata sandi ikut terkirim. Solusinya: **pakai model berbeda untuk input dan output**.

## Kode lengkap

Contoh pertama menunjukkan masalahnya (`main_bocor.py`):

```python title="main_bocor.py"
--8<-- "fastapi/03-data-validasi/response-model/main_bocor.py"
```

Contoh kedua adalah versi yang benar (`main.py`):

```python title="main.py"
--8<-- "fastapi/03-data-validasi/response-model/main.py"
```

## Penjelasan kode

### Masalah: model yang sama untuk input dan output

Di `main_bocor.py`, endpoint mengembalikan `data` apa adanya. Semua field, termasuk `kata_sandi`, ikut keluar. Hasil uji ada di bagian [Mencoba request](#mencoba-request).

### Dua model terpisah

```python
class AkunBaru(BaseModel):
    nama: str
    email: str
    kata_sandi: str


class AkunPublik(BaseModel):
    id: int
    nama: str
    email: str
```

`AkunBaru` menggambarkan data **masuk** (ada `kata_sandi`, tanpa `id`). `AkunPublik` menggambarkan data **keluar** (ada `id`, tanpa `kata_sandi`).

### `response_model` pada dekorator

```python
@app.post("/akun", response_model=AkunPublik, status_code=201)
def buat_akun(data: AkunBaru):
    akun = {"id": len(akun_db) + 1, **data.model_dump()}
    akun_db.append(akun)
    return akun
```

- `response_model=AkunPublik` adalah parameter **dekorator**, bukan parameter fungsi.
- Fungsi mengembalikan `dict` lengkap (berisi `kata_sandi`), tetapi FastAPI menyaringnya sesuai `AkunPublik` sebelum dikirim.
- `**data.model_dump()` menyalin semua pasangan kunci-nilai dari dict hasil `model_dump()` ke dict baru.
- `akun_db` adalah `list` biasa di memori sebagai basis data tiruan. Datanya hilang saat server dimulai ulang. Menyimpan kata sandi mentah seperti ini hanya untuk contoh; praktik aman dibahas di modul autentikasi.

### Response model untuk `list`

```python
@app.get("/akun", response_model=list[AkunPublik])
def daftar_akun():
    return akun_db
```

`response_model` menerima tipe apa pun yang sah untuk field Pydantic, termasuk `list[AkunPublik]`. Setiap elemen disaring satu per satu.

### Mengatur isi response

```python
class Profil(BaseModel):
    nama: str
    bio: str | None = None
    kota: str = "Tidak diketahui"
```

- `response_model_exclude_unset=True`: field yang **tidak pernah diisi** (hanya terisi dari nilai default) dibuang dari response.
- `response_model_exclude={"kota"}`: field yang disebut dibuang. Nilainya berupa `set` nama field.

Dokumentasi FastAPI menyebut keduanya sebagai jalan pintas. Untuk kasus yang lebih besar, ia menganjurkan membuat beberapa kelas model, sebab skema di dokumentasi otomatis tetap menggambarkan model lengkap.

### Data keluar yang tidak sesuai model

```python
@app.get("/rusak", response_model=AkunPublik)
def respons_rusak():
    return {"id": 1, "nama": "Tanpa email"}
```

Field `email` wajib di `AkunPublik` tetapi tidak ada. FastAPI menolak mengirimnya, dan klien menerima `500`. Ini kesalahan **server**, bukan `422`, karena kesalahannya ada di kode kita, bukan di request klien.

## Alternatif: pewarisan dan anotasi tipe kembalian

FastAPI juga bisa membaca response model dari anotasi tipe kembalian. Bila kelasnya diturunkan, anotasi tetap benar menurut editor:

```python title="main_pewarisan.py"
--8<-- "fastapi/03-data-validasi/response-model/main_pewarisan.py"
```

`AkunBaru` mewarisi `AkunDasar` dan menambah `kata_sandi`. Fungsi dianotasi `-> AkunDasar`, sehingga response hanya berisi field `AkunDasar`.

Dua hal dari dokumentasi FastAPI yang tidak dijalankan di sini: bila `response_model` dan anotasi tipe kembalian sama-sama ditulis, `response_model` yang diprioritaskan; dan `response_model=None` mematikan pemrosesan ini.

## Menjalankan

Siapkan venv seperti di [Instalasi dan Virtual Environment](../01-pengenalan/instalasi-dan-venv.md), lalu:

```powershell
fastapi dev main.py
```

Untuk contoh lain, ganti `main.py` dengan `main_bocor.py` atau `main_pewarisan.py`. Server berjalan di `http://127.0.0.1:8000` dan dokumentasi interaktif ada di `/docs`.

## Mencoba request

Simpan body ini sebagai `akun.json`:

```json title="akun.json"
{"nama":"Budi","email":"budi@contoh.id","kata_sandi":"rahasia123"}
```

### Dengan model terpisah (`main.py`)

```powershell
curl.exe -i -X POST http://127.0.0.1:8000/akun -H "Content-Type: application/json" -d "@akun.json"
```

Status `HTTP/1.1 201 Created`, isi:

```json
{"id":1,"nama":"Budi","email":"budi@contoh.id"}
```

Tidak ada `kata_sandi`. Daftar akun:

```powershell
curl.exe http://127.0.0.1:8000/akun
```

```json
[{"id":1,"nama":"Budi","email":"budi@contoh.id"}]
```

### Tanpa filter (`main_bocor.py`)

Dengan body yang sama (diuji dengan `TestClient`):

```json
{"nama":"Budi","email":"budi@contoh.id","kata_sandi":"rahasia123"}
```

Kata sandi ikut keluar. Inilah kebocoran yang dicegah response model.

### Dengan pewarisan (`main_pewarisan.py`)

Diuji dengan `TestClient`, hasilnya `201` dengan isi:

```json
{"nama":"Budi","email":"budi@contoh.id"}
```

### Mengatur isi response (`Profil`)

Hasil uji dengan `TestClient`. Data `budi` tidak punya `bio`, sedangkan `sari` mengisi `bio` dan `kota` secara eksplisit:

| Endpoint | Hasil |
|---|---|
| `/profil/budi` | `{"nama":"Budi","bio":null,"kota":"Bandung"}` |
| `/profil/budi/ringkas` | `{"nama":"Budi","kota":"Bandung"}` |
| `/profil/sari` | `{"nama":"Sari","bio":null,"kota":"Tidak diketahui"}` |
| `/profil/sari/ringkas` | `{"nama":"Sari","bio":null,"kota":"Tidak diketahui"}` |
| `/profil/budi/tanpa-kota` | `{"nama":"Budi","bio":null}` |

Perhatikan baris `sari/ringkas`: `bio` dan `kota` tetap muncul walau nilainya sama dengan default, karena **diisi eksplisit** di data `sari`. `exclude_unset` membedakan "tidak diisi" dari "diisi dengan nilai yang kebetulan sama dengan default".

### Data keluar yang tidak sesuai

```powershell
curl.exe -i http://127.0.0.1:8000/rusak
```

```text
HTTP/1.1 500 Internal Server Error
Internal Server Error
```

Di terminal server tercatat `ResponseValidationError` (lewat `fastapi dev`; baris log lengkapnya tidak ditampilkan di sini).

### Dokumentasi otomatis

Hasil `/openapi.json`: response `201` untuk `POST /akun` mengacu ke skema `AkunPublik`, dan skema `AkunBaru` (dengan `kata_sandi`) terdaftar terpisah untuk body request. Tampilan visual di Swagger UI **belum diverifikasi** lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Mengembalikan model input langsung | Data sensitif ikut keluar (teruji di `main_bocor.py`). |
| Memasang `response_model` pada fungsi, bukan dekorator | Parameter ini milik dekorator (`@app.post(...)`). |
| Data yang dikembalikan kekurangan field wajib | `500`, bukan `422` (teruji di `/rusak`). |
| Mengira `response_model_exclude` menyembunyikan field dari dokumentasi | Dokumentasi FastAPI menyatakan skema tetap menggambarkan model lengkap. Untuk skema yang rapi, buat model terpisah. Perilaku skema ini tidak dijalankan di sini. |
| Mengira `exclude_unset` membuang semua nilai default | Hanya nilai yang tidak diisi; nilai yang diisi eksplisit tetap muncul (teruji di `sari/ringkas`). |

## Latihan

1. **Dasar.** Buat model `Buku` (`judul`, `penulis`, `stok` berdefault 0, `catatan` opsional). Endpoint `GET /buku` mengembalikan `list` dict yang masih memuat `harga_modal`. Pasang `response_model=list[Buku]`. Apakah `harga_modal` muncul?
2. **Filter.** Dari model yang sama, kembalikan hanya `judul` lewat `response_model_include`.
3. **Null.** Buat endpoint yang membuang field bernilai `null` dengan `response_model_exclude_none=True`.
4. **Analisis.** Pada `main_bocor.py`, apa saja yang perlu diubah agar `kata_sandi` tidak bocor? Tulis ringkas.

??? success "Kunci jawaban"
    Jawaban 1 sampai 3 dijalankan dengan `TestClient`. Jawaban 4 adalah penalaran dari kode di halaman.

    ```python
    from fastapi import FastAPI
    from pydantic import BaseModel

    app = FastAPI()


    class Buku(BaseModel):
        judul: str
        penulis: str
        stok: int = 0
        catatan: str | None = None


    db = [{"judul": "A", "penulis": "X", "harga_modal": 5000, "stok": 3}]


    @app.get("/buku", response_model=list[Buku])
    def daftar():
        return db


    @app.get("/buku/0", response_model=Buku, response_model_exclude_none=True)
    def satu():
        return db[0]


    @app.get("/buku/1", response_model=Buku, response_model_include={"judul"})
    def judul_saja():
        return db[0]
    ```

    1. `harga_modal` **tidak** muncul. Hasil: `[{"judul":"A","penulis":"X","stok":3,"catatan":null}]`.
    2. `/buku/1` menghasilkan `{"judul":"A"}`.
    3. `/buku/0` menghasilkan `{"judul":"A","penulis":"X","stok":3}`; `catatan` yang `null` dibuang.
    4. Buat model output tanpa `kata_sandi` (mis. `AkunPublik`) dan pasang `response_model=AkunPublik` pada dekorator, atau pakai pewarisan dengan anotasi `-> AkunDasar`.

## Ringkasan

- Response model adalah bentuk data **keluar**; FastAPI memvalidasi dan memfilter data sesuai model itu.
- Pisahkan model input dan output agar data sensitif tidak bocor.
- `response_model` adalah parameter dekorator dan menerima tipe seperti `list[Model]`.
- Pewarisan plus anotasi tipe kembalian adalah alternatif yang ramah editor.
- `response_model_exclude_unset`, `_exclude_none`, `_include`, dan `_exclude` mengatur isi response, tetapi model terpisah lebih rapi untuk kasus besar.
- Data keluar yang tidak sesuai model menghasilkan `500`.

## Langkah berikutnya

Kembali ke daftar materi di [Modul 03: Data dan Validasi](index.md). Materi berikutnya adalah proyek praktik tahap 1.
