# Validasi Field

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Membedakan validasi tipe dari validasi aturan nilai.
- [ ] Memasang batasan panjang, rentang angka, dan pola teks dengan `Field`.
- [ ] Menulis aturan sendiri dengan `field_validator`.
- [ ] Membaca jenis error validasi (`type`) dan konteksnya (`ctx`).
- [ ] Mengenali jebakan umum: default yang tidak divalidasi dan spasi yang ikut dihitung.

## Prasyarat

- Sudah membaca [Model Pydantic](model-pydantic.md).
- Pemahaman dasar `class` dan dekorator di Python.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, dan **Pydantic 2.14.1** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Sejauh ini model hanya memeriksa **tipe**: `umur` harus bilangan bulat, `nama` harus teks. Tetapi tipe yang benar belum tentu nilai yang masuk akal. Umur `-5` adalah bilangan bulat yang sah, begitu pula nama berupa teks kosong.

**Validasi field** menambahkan aturan pada nilai sebuah field, misalnya "minimal 3 karakter" atau "antara 17 dan 100". Ada dua alat:

| Alat | Cara kerja | Cocok untuk |
|---|---|---|
| `Field(...)` | Aturan ditulis sebagai argumen, tanpa kode | Batas panjang, rentang angka, pola teks |
| `@field_validator` | Aturan ditulis sebagai fungsi Python | Aturan yang tidak bisa ditulis sebagai angka atau pola |

Dokumentasi Pydantic menyebut validator sebagai cara menerapkan batasan yang lebih kompleks daripada yang tersedia lewat constraint `Field`. Karena itu, pakai `Field` dulu, dan baru beralih ke validator bila perlu.

Dokumentasi FastAPI juga mencatat bahwa `Field` diimpor dari `pydantic` (bukan dari `fastapi`).

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/03-data-validasi/validasi-field/main.py"
```

## Penjelasan kode

### Impor

```python
from pydantic import BaseModel, Field, field_validator
```

Tiga hal dari Pydantic: `BaseModel` untuk model, `Field` untuk aturan deklaratif, dan `field_validator` untuk aturan berupa fungsi.

### Aturan lewat `Field`

```python
nama: str = Field(min_length=3, max_length=30, description="Nama lengkap")
umur: int = Field(ge=17, le=100)
kode_kelas: str = Field(pattern=r"^[A-Z]{2}\d{3}$", description="Contoh: IF101")
nilai_awal: float = Field(default=0, ge=0, le=100)
minat: list[str] = Field(default=[], max_length=3)
```

| Argumen | Artinya | Berlaku untuk |
|---|---|---|
| `min_length`, `max_length` | Panjang minimal dan maksimal | Teks, dan juga jumlah item list |
| `ge`, `le` | *Greater or equal* (lebih besar atau sama dengan), *less or equal* (lebih kecil atau sama dengan) | Angka |
| `gt`, `lt` | *Greater than*, *less than* (tanpa "sama dengan") | Angka |
| `pattern` | Pola teks berupa *regular expression* | Teks |
| `default` | Nilai bawaan. Field menjadi opsional | Semua |
| `description` | Keterangan untuk dokumentasi otomatis | Semua |

Beberapa catatan:

- Field tanpa `default` tetap **wajib**, seperti `nama` dan `umur`. `Field(min_length=3)` hanya menambahkan aturan, bukan membuat field opsional.
- `umur: int = Field(ge=17, le=100)` berarti 17 dan 100 sendiri **diterima** (batas inklusif). Dengan `gt` dan `lt`, batasnya tidak ikut.
- `r"^[A-Z]{2}\d{3}$"` adalah pola: `^` awal teks, `[A-Z]{2}` tepat dua huruf kapital, `\d{3}` tepat tiga angka, `$` akhir teks. Jadi `IF101` cocok, tetapi `if101` dan `IF10` tidak. Awalan `r` membuat teks itu *raw string*, sehingga `\d` tidak ditafsirkan sebagai karakter escape Python.

!!! note "Sumber penjelasan"
    Halaman dokumentasi Pydantic dan FastAPI yang saya periksa hanya mencontohkan sebagian argumen ini (antara lain `gt`, `lt`, `max_length`, `default`, `description`). Perilaku `ge`, `le`, `min_length`, dan `pattern` yang dijelaskan di sini saya buktikan lewat pengujian langsung di bawah.

### Aturan lewat `field_validator`

```python
@field_validator("nama")
@classmethod
def nama_tanpa_angka(cls, nilai: str) -> str:
    if any(huruf.isdigit() for huruf in nilai):
        raise ValueError("nama tidak boleh mengandung angka")
    return nilai.title()
```

| Bagian | Fungsinya |
|---|---|
| `@field_validator("nama")` | Memasang fungsi ini pada field `nama` |
| `@classmethod` | Diwajibkan oleh Pydantic di bawah `@field_validator`. Karena itu parameter pertama bernama `cls`, bukan `self` |
| `nilai: str` | Nilai field yang akan diperiksa |
| `any(huruf.isdigit() for huruf in nilai)` | `True` jika ada minimal satu karakter angka |
| `raise ValueError(...)` | Menyatakan nilai tidak valid. Pesannya masuk ke error |
| `return nilai.title()` | **Wajib mengembalikan nilai.** Di sini nilai sekalian dirapikan: setiap kata diawali huruf kapital |

Dokumentasi Pydantic menekankan bahwa validator harus mengembalikan nilai hasil validasi, dan bahwa nilai itu boleh berbeda dari inputnya.

### Urutan pemeriksaan

```text
Input "budi santoso"
   │
   ▼ 1. cek tipe          → harus str
   ▼ 2. cek Field         → min_length=3, max_length=30
   ▼ 3. field_validator   → tanpa angka, lalu .title()
   ▼
"Budi Santoso"
```

Urutan ini berlaku untuk validator mode bawaan (`after`), yang menurut dokumentasi berjalan setelah validasi internal Pydantic. Mode `before` berjalan lebih awal (lihat latihan 4).

## Menjalankan aplikasi

```bash
fastapi dev main.py
```

Contoh di bawah memakai port `8000`; sesuaikan bila berbeda.

## Mencoba request

Simpan body ke file lalu kirim dengan `-d "@file"`, seperti di [Request Body](request-body.md#mencoba-request). Contoh `valid.json`:

```json
{"nama":"budi santoso","umur":20,"kode_kelas":"IF101","nilai_awal":85.5,"minat":["web","data"]}
```

```bash
curl -i -X POST "http://127.0.0.1:8000/pendaftaran" -H "Content-Type: application/json" -d "@valid.json"
```

Hasil nyata (`201 Created`). Perhatikan `nama` yang dikirim huruf kecil kini diubah validator menjadi `Budi Santoso`:

```json
{"nama":"Budi Santoso","umur":20,"kode_kelas":"IF101","nilai_awal":85.5,"minat":["web","data"]}
```

Body lain yang diterima (`201`):

| Body | Hasil |
|---|---|
| Hanya `nama`, `umur` 17, `kode_kelas` | `nilai_awal` `0` dan `minat` `[]` (nilai default) |
| `nama` `"Abc"` (3 huruf), `umur` 100, `nilai_awal` 100, `minat` berisi 3 item | Diterima: semua berada tepat di batas |

## Membaca error validasi

Semua kasus ini mengembalikan `422`, dengan `loc` yang diawali `body`. Hasil nyata:

| Input yang salah | `type` | Pesan (`msg`) | `ctx` |
|---|---|---|---|
| `nama` `"ab"` | `string_too_short` | String should have at least 3 characters | `{"min_length":3}` |
| `nama` 33 huruf | `string_too_long` | String should have at most 30 characters | `{"max_length":30}` |
| `umur` 16 | `greater_than_equal` | Input should be greater than or equal to 17 | `{"ge":17}` |
| `umur` 101 | `less_than_equal` | Input should be less than or equal to 100 | `{"le":100}` |
| `nilai_awal` 101 | `less_than_equal` | Input should be less than or equal to 100 | `{"le":100.0}` |
| `kode_kelas` `"if101"` atau `"IF10"` | `string_pattern_mismatch` | String should match pattern ... | `{"pattern":"..."}` |
| `minat` 4 item | `too_long` | List should have at most 3 items after validation, not 4 | `max_length`, `actual_length` |
| `nama` `"Budi2"` | `value_error` | Value error, nama tidak boleh mengandung angka | `{"error":{}}` |

Cara membacanya:

- `type` adalah jenis aturan yang dilanggar, berguna untuk dibaca program klien.
- `msg` adalah penjelasan untuk manusia (berbahasa Inggris, karena berasal dari Pydantic).
- `ctx` memuat nilai batas yang dilanggar.
- Untuk validator buatanmu sendiri, `type` adalah `value_error` dan pesanmu muncul di `msg` dengan awalan `Value error, `. Bagian `ctx.error` kosong pada response, jadi bacalah pesannya dari `msg`.

Contoh body lengkap untuk `nama` `"ab"`:

```json
{"detail":[{"type":"string_too_short","loc":["body","nama"],"msg":"String should have at least 3 characters","input":"ab","ctx":{"min_length":3}}]}
```

### Beberapa pelanggaran sekaligus

Body `{"nama":"ab","umur":5,"kode_kelas":"x"}` melanggar tiga aturan. Pada pengujian, ketiganya dilaporkan dalam satu response `422`: `string_too_short` pada `nama`, `greater_than_equal` pada `umur`, dan `string_pattern_mismatch` pada `kode_kelas`. Klien dapat memperbaiki semuanya sekaligus.

## Dua jebakan yang teramati

### 1. Nilai default tidak divalidasi

`nilai_awal` didefinisikan `Field(default=0, ge=0, le=100)`. Ketika klien tidak mengirimnya, hasilnya `"nilai_awal":0` (bilangan bulat). Sebaliknya, ketika klien mengirim `100`, hasilnya `100.0` (desimal). Default `0` tidak dikonversi ke `float` karena nilai default tidak ikut divalidasi. Dokumentasi Pydantic menyatakan hal yang sama: secara bawaan nilai default tidak divalidasi. Pelajaran: tulis default yang sudah sesuai tipe dan aturannya (misalnya `0.0`).

### 2. Spasi ikut dihitung

Body `{"nama":"  ab ", ...}` ternyata **diterima** (`201`), dengan hasil `"nama":"  Ab "`. Teks `"  ab "` berisi 5 karakter (termasuk spasi), sehingga lolos `min_length=3`, padahal isinya hanya dua huruf. Spasi di awal dan akhir juga ikut tersimpan. Cara mengatasinya ada di latihan 4.

## Dokumentasi otomatis

Aturan `Field` ikut tercatat di skema. Pada pengujian, `/openapi.json` memuat untuk `nama`: `minLength` 3, `maxLength` 30, dan `description`; untuk `umur`: `minimum` 17 dan `maximum` 100; untuk `kode_kelas`: `pattern`; untuk `minat`: `maxItems` 3; dan field wajibnya `nama`, `umur`, `kode_kelas`. Jadi klien dapat membaca aturan tanpa membaca kode. Aturan di `field_validator` **tidak** muncul di skema, karena berupa kode Python. Tampilan visualnya di Swagger UI belum saya periksa.

## Kesalahan umum

Semua kasus berikut dijalankan dan dicatat apa adanya, kecuali yang disebut sebaliknya.

### 1. Mengira batas `ge`/`le` bukan inklusif

`umur` 17 dan 100 diterima, sedangkan 16 dan 101 ditolak. Jika kamu ingin batas yang tidak ikut, gunakan `gt`/`lt`.

### 2. Aturan `Field` pada field wajib dianggap membuatnya opsional

`nama: str = Field(min_length=3)` tetap wajib. Pada pengujian, field wajibnya `nama`, `umur`, dan `kode_kelas`. Untuk membuat opsional, tambahkan `default`.

### 3. Lupa mengembalikan nilai di validator

Dokumentasi Pydantic menyatakan bahwa validator harus mengembalikan nilai. Pada kode di halaman ini, hasil `return nilai.title()` itulah yang menjadi nilai field. Akibat lupa `return` tidak saya jalankan, jadi saya tidak mengklaim bentuk error-nya.

### 4. Validator tanpa `@classmethod`

Dokumentasi menyatakan `@classmethod` dibutuhkan di bawah `@field_validator`. Kasus lupa tidak saya jalankan.

### 5. Membaca `ctx.error` di response untuk pesan validator

Pada response validator buatan sendiri, `ctx.error` kosong (`{}`). Pesannya ada di `msg`.

## Latihan

1. **Dasar.** Tambahkan field `nim: str` yang harus tepat 8 karakter dan hanya berisi angka. Uji `"12345678"`, `"1234567"`, dan `"1234abcd"`.
2. **Menengah.** Tambahkan `ipk: float` dengan rentang 0 sampai 4 (inklusif). Uji `3.5`, `0`, dan `4.5`.
3. **Menengah.** Buat validator untuk `minat` yang merapikan setiap item: hapus spasi di tepi dan ubah ke huruf kecil. Uji `[" Web ", "DATA"]`.
4. **Tantangan.** Perbaiki jebakan spasi: jadikan `"  ab "` ditolak (karena isinya hanya 2 huruf), dan `"  abc "` diterima sebagai `"abc"`. Petunjuk: validator dengan `mode="before"`.

??? success "Kunci jawaban (sudah dijalankan)"
    1. Kode:

        ```python
        nim: str = Field(min_length=8, max_length=8, pattern=r"^\d+$")
        ```

        `"12345678"` diterima. `"1234567"` ditolak `string_too_short`. `"1234abcd"` ditolak `string_pattern_mismatch`.
    2. Kode: `ipk: float = Field(ge=0, le=4)`. `3.5` diterima, `0` diterima (menjadi `0.0`), `4.5` ditolak `less_than_equal`.
    3. Kode:

        ```python
        @field_validator("minat")
        @classmethod
        def rapikan(cls, nilai: list[str]) -> list[str]:
            return [m.strip().lower() for m in nilai]
        ```

        `[" Web ", "DATA"]` menjadi `["web", "data"]`.
    4. Kode:

        ```python
        nama: str = Field(min_length=3)

        @field_validator("nama", mode="before")
        @classmethod
        def potong_spasi(cls, nilai):
            return nilai.strip() if isinstance(nilai, str) else nilai
        ```

        Validator `before` berjalan lebih dulu, sehingga `"  ab "` menjadi `"ab"` lalu ditolak `string_too_short`. `"  abc "` menjadi `"abc"` dan diterima. `isinstance` menjaga agar nilai bukan teks tetap diserahkan ke pemeriksaan tipe.

    Semua jawaban diuji dengan `TestClient` dari FastAPI.

## Ringkasan

- Tipe yang benar belum menjamin nilai yang masuk akal. Validasi field menambahkan aturan pada nilai.
- `Field(...)` untuk aturan deklaratif: `min_length`, `max_length`, `ge`, `le`, `gt`, `lt`, `pattern`, dan `default`. `description` ikut ke dokumentasi.
- `@field_validator` + `@classmethod` untuk aturan berupa kode. Validator wajib mengembalikan nilai, dan boleh mengubahnya.
- Error validasi memuat `type`, `msg`, dan `ctx`; beberapa pelanggaran dilaporkan sekaligus.
- Batas `ge`/`le` inklusif. Aturan `Field` tidak membuat field menjadi opsional.
- Jebakan: nilai default tidak divalidasi, dan spasi ikut dihitung dalam panjang teks.
- Aturan `Field` tercatat di skema dokumentasi, sedangkan aturan validator tidak.

## Langkah berikutnya

Kembali ke daftar materi di [Modul 03: Data dan Validasi](index.md). Materi berikutnya adalah validasi path dan query parameter.
