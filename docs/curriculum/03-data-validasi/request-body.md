# Request Body

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan apa itu request body dan kapan dipakai.
- [ ] Menerima body JSON di endpoint FastAPI memakai model Pydantic.
- [ ] Membedakan field wajib dan opsional pada body.
- [ ] Mengirim request ber-body dengan `curl` dengan benar.
- [ ] Membaca error `422` yang berasal dari body.
- [ ] Menggabungkan body, path parameter, dan query parameter dalam satu endpoint.

## Prasyarat

- Sudah menyelesaikan [Modul 02: Dasar Routing](../02-dasar-routing/index.md), terutama [Path Parameter](../02-dasar-routing/path-parameter.md) dan [Query Parameter](../02-dasar-routing/query-parameter.md).
- Class dan type hints di Python.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, dan **Pydantic 2.14.1** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Sejauh ini, semua data yang kamu kirim ke API terselip di URL: path parameter untuk menunjuk sumber daya, query parameter untuk opsi. Itu cukup untuk data kecil. Tetapi untuk membuat tugas baru, kamu perlu mengirim banyak isian sekaligus: judul, status, catatan. Menjejalkannya ke URL tidak praktis.

Solusinya adalah **request body**: data yang dikirim **di dalam isi request**, terpisah dari URL. Dokumentasi resmi FastAPI menyebut request body sebagai data yang dikirim klien ke API.

```text
POST /tugas HTTP/1.1                       ← baris request (method + path)
Content-Type: application/json             ← header
                                           ← baris kosong
{"judul": "Belajar FastAPI"}               ← body
```

Pada [HTTP dan REST](../01-pengenalan/http-dan-rest.md) kamu sudah mengenal bagian-bagian request ini. Body adalah bagian terakhir.

Poin penting tentang body:

| Hal | Penjelasan |
|---|---|
| Method yang lazim | `POST`, `PUT`, `PATCH`, dan `DELETE`. `POST` paling umum untuk membuat data |
| Dengan `GET` | Menurut dokumentasi resmi, mengirim body dengan `GET` tidak didefinisikan jelas dalam spesifikasi dan tidak dianjurkan |
| Format | Pada materi ini selalu **JSON** |

Cara mendeklarasikan bentuk body di FastAPI adalah dengan **model Pydantic**, yaitu sebuah class yang menyebutkan field dan tipenya. Model dibahas lebih dalam pada materi berikutnya di modul ini; di sini kamu cukup mengenal bentuk dasarnya.

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/03-data-validasi/request-body/main.py"
```

## Penjelasan kode

### Mendefinisikan bentuk body

```python
from pydantic import BaseModel


class TugasBaru(BaseModel):
    judul: str
    selesai: bool = False
    catatan: str | None = None
```

| Bagian | Artinya |
|---|---|
| `class TugasBaru(BaseModel)` | Membuat model. `BaseModel` dari Pydantic membuat class ini bisa memvalidasi data |
| `judul: str` | Field **wajib** bertipe teks, karena tidak punya nilai default |
| `selesai: bool = False` | Field **opsional** bertipe boolean. Jika tidak dikirim, nilainya `False` |
| `catatan: str \| None = None` | Field **opsional** yang boleh teks atau tidak ada (`None`) |

Aturannya sama dengan [Query Parameter](../02-dasar-routing/query-parameter.md): tanpa nilai default berarti wajib, dengan nilai default berarti opsional.

### Memakai model sebagai body

```python
@app.post("/tugas", status_code=201)
def buat_tugas(tugas: TugasBaru):
    return {"pesan": "Tugas diterima", "data": tugas.model_dump()}
```

| Bagian | Fungsinya |
|---|---|
| `tugas: TugasBaru` | Karena tipenya model Pydantic, FastAPI memperlakukan `tugas` sebagai **request body** |
| `status_code=201` | Status sukses `201 Created`, seperti di [HTTP dan REST](../01-pengenalan/http-dan-rest.md) |
| `tugas.model_dump()` | Mengubah objek model menjadi `dict` Python biasa. Field juga bisa dibaca langsung, misalnya `tugas.judul` |

Dokumentasi resmi merumuskan aturan pengenalan parameter sebagai berikut:

| Jika parameter... | FastAPI membacanya sebagai |
|---|---|
| ada di path (`{...}`) | path parameter |
| bertipe tunggal (`int`, `str`, `bool`, dan sejenisnya) | query parameter |
| bertipe model Pydantic | request body |

### Body + path + query sekaligus

```python
@app.put("/tugas/{tugas_id}")
def ganti_tugas(tugas_id: int, tugas: TugasBaru, simpan: bool = False):
    return {"tugas_id": tugas_id, "simpan": simpan, "data": tugas.model_dump()}
```

Tiga sumber data dalam satu endpoint:

- `tugas_id` ada di path, jadi dari **path**.
- `tugas` bertipe model, jadi dari **body**.
- `simpan` bertipe tunggal dan tidak ada di path, jadi dari **query**.

### Hubungan antarbagian

```text
Request : POST /tugas   Content-Type: application/json
          {"judul": "Belajar FastAPI"}
             │  FastAPI membaca body sebagai JSON
             ▼
Validasi : cocokkan dengan TugasBaru  (judul wajib, selesai default False, ...)
             ▼
Fungsi   : buat_tugas(tugas=TugasBaru(judul="Belajar FastAPI", selesai=False, catatan=None))
             ▼
Response : 201 + {"pesan":"Tugas diterima","data":{...}}
```

## Menjalankan aplikasi

```bash
fastapi dev main.py
```

Contoh di bawah memakai port `8000`; sesuaikan bila berbeda.

## Mencoba request

Mengirim JSON lewat `curl` sering merepotkan karena aturan tanda kutip berbeda di tiap shell. Cara paling aman lintas shell: **simpan body ke file**, lalu kirim file itu dengan `-d "@nama-file"`.

Buat file `tugas.json`:

```json
{"judul": "Belajar FastAPI", "selesai": true, "catatan": "Bab 3"}
```

Kirim (pengguna PowerShell: ketik `curl.exe`):

```bash
curl -i -X POST "http://127.0.0.1:8000/tugas" -H "Content-Type: application/json" -d "@tugas.json"
```

| Opsi | Artinya |
|---|---|
| `-X POST` | Memakai method `POST` |
| `-H "Content-Type: application/json"` | Memberi tahu server bahwa body berformat JSON |
| `-d "@tugas.json"` | Mengirim isi file sebagai body |

Hasil dari eksekusi nyata:

```text
HTTP/1.1 201 Created
```

```json
{"pesan":"Tugas diterima","data":{"judul":"Belajar FastAPI","selesai":true,"catatan":"Bab 3"}}
```

Beberapa kasus lain yang diuji:

| Body yang dikirim | Status | Hasil |
|---|---|---|
| `{"judul": "Belajar FastAPI"}` | `201` | `selesai` jadi `false` dan `catatan` jadi `null` (nilai default) |
| `{"judul": "x", "selesai": "yes"}` | `201` | `selesai` dikonversi menjadi `true` |
| `{"judul": "x", "umur": 5}` | `201` | Field `umur` yang tidak dikenal **diabaikan**, tidak muncul di `data` |

Poin terakhir perlu diingat: field berlebih tidak menimbulkan error dan tidak ikut diproses.

### Body + path + query

File `tugas.json` yang sama dikirim ke endpoint `PUT`:

```bash
curl -i -X PUT "http://127.0.0.1:8000/tugas/7?simpan=true" -H "Content-Type: application/json" -d "@tugas.json"
```

Hasil nyata (`200 OK`):

```json
{"tugas_id":7,"simpan":true,"data":{"judul":"Belajar FastAPI","selesai":true,"catatan":"Bab 3"}}
```

`7` dari path, `true` dari query, dan `data` dari body.

## Validasi body

Sama seperti path dan query parameter, FastAPI mengonversi dan memvalidasi body berdasarkan tipenya. Perbedaannya, lokasi kesalahan di `loc` kini diawali `body`.

### Field wajib hilang

Body `{"selesai": true}` (tanpa `judul`):

```json
{"detail":[{"type":"missing","loc":["body","judul"],"msg":"Field required","input":{"selesai":true}}]}
```

Status `422`. `loc` berisi `["body","judul"]`: field `judul` di dalam body. `input` memperlihatkan body yang diterima.

### Tipe salah

Body `{"judul": 123}`:

```json
{"detail":[{"type":"string_type","loc":["body","judul"],"msg":"Input should be a valid string","input":123}]}
```

Perhatikan bahwa angka `123` **tidak** otomatis diubah menjadi teks `"123"` untuk field bertipe `str`. Pada pengujian, `{"judul": null}` juga ditolak dengan `string_type`, sedangkan `{"judul": "x", "catatan": null}` diterima karena `catatan` memang boleh `None`.

Untuk field `bool`, nilai seperti `"yes"` dikonversi, tetapi `"ya"` ditolak dengan `bool_parsing` (`422`), sama seperti di query parameter.

### Beberapa kesalahan sekaligus

`PUT /tugas/x` dengan body tanpa `judul` menghasilkan `422` berisi **dua** error dalam satu response: `["path","tugas_id"]` (`int_parsing`) dan `["body","judul"]` (`missing`). Semua kesalahan dilaporkan sekaligus.

## Dokumentasi otomatis

Pada pengujian, `/openapi.json` mencatat model `TugasBaru` dengan `judul` sebagai satu-satunya field wajib (`"required": ["judul"]`), `selesai` bertipe `boolean` dengan default `false`, dan `catatan` bertipe `string` atau `null`. Request body pada `POST /tugas` tercatat wajib dengan tipe konten `application/json`. Jadi bentuk body terbaca di dokumentasi tanpa kamu menulisnya. Cara membuka dokumentasi ada di [Dokumentasi Interaktif](../01-pengenalan/dokumentasi-interaktif.md); tampilan visualnya di browser belum saya periksa.

## Kesalahan umum

Semua kasus berikut dijalankan dan dicatat apa adanya.

### 1. Lupa header `Content-Type`

Jika `curl` memakai `-d` tanpa `-H "Content-Type: application/json"`, `curl` mengirim tipe konten untuk form, bukan JSON. Pada pengujian, hasilnya `422`:

```json
{"detail":[{"type":"model_attributes_type","loc":["body"],"msg":"Input should be a valid dictionary or object to extract fields from","input":"{\"judul\": \"Belajar FastAPI\"}"}]}
```

Perhatikan `input`: body diterima sebagai **teks utuh**, bukan objek. **Solusi:** selalu sertakan `-H "Content-Type: application/json"`. Penjelasan bahwa `curl -d` memakai tipe konten form secara bawaan adalah pengetahuan umum tentang `curl`, bukan sesuatu yang saya periksa di dokumentasinya.

### 2. JSON rusak

Body `{"judul": }` menghasilkan `422` dengan `type` `json_invalid` dan `msg` `JSON decode error`. **Solusi:** periksa tanda kutip, koma, dan kurung. Tulis body di file dan periksa dengan editor.

### 3. Tidak mengirim body

`POST /tugas` tanpa `-d` menghasilkan `422`:

```json
{"detail":[{"type":"missing","loc":["body"],"msg":"Field required","input":null}]}
```

Bedanya dengan field hilang: `loc` hanya `["body"]`, tanpa nama field. Body kosong dari file juga menghasilkan error yang sama.

### 4. Field berlebih diabaikan diam-diam

Salah ketik nama field, misalnya `judull`, tidak menimbulkan error untuk field yang berlebih; yang muncul justru error `missing` untuk `judul` yang asli. Kasus `judull` sendiri tidak saya jalankan; perilakunya mengikuti hasil `umur` yang teruji (field tak dikenal diabaikan) dan hasil `missing` pada body tanpa `judul`.

### 5. Mencoba `GET` dengan body

Endpoint `/tugas` hanya didaftarkan untuk `POST`. Pada pengujian, `GET /tugas` menghasilkan `405 Method Not Allowed`.

## Latihan

1. **Dasar.** Tambahkan field `prioritas: int = 1` pada `TugasBaru`. Kirim `{"judul": "x"}` dan lihat nilai `prioritas`. Lalu kirim `{"judul": "x", "prioritas": "tinggi"}`.
2. **Menengah.** Buat model `Catatan` dengan satu field `isi: str`, dan endpoint `POST /catatan` yang mengembalikan `{"panjang": <jumlah huruf isi>}`. Uji dengan `{"isi": "halo dunia"}`.
3. **Menengah.** Prediksikan hasil `PUT /tugas/7?simpan=true` dengan body `{"judul": "Rapikan meja"}`, lalu jalankan.
4. **Tantangan.** Apa perbedaan hasil antara mengirim `{"judul": null}` dan `{"judul": "x", "catatan": null}`? Jelaskan mengapa.

??? success "Kunci jawaban (sudah dijalankan)"
    1. Kode: tambahkan `prioritas: int = 1` pada model. `{"judul": "x"}` menghasilkan `prioritas` bernilai `1`. `{"judul": "x", "prioritas": "tinggi"}` menghasilkan `422` dengan `type` `int_parsing` dan `loc` `["body","prioritas"]`.
    2. Kode:

        ```python
        class Catatan(BaseModel):
            isi: str


        @app.post("/catatan")
        def catatan(c: Catatan):
            return {"panjang": len(c.isi)}
        ```

        `{"isi": "halo dunia"}` menghasilkan `{"panjang":10}`.
    3. Hasilnya `200` dengan `tugas_id` 7, `simpan` `true`, dan `data` berisi `judul` "Rapikan meja", `selesai` `false`, `catatan` `null` (nilai default). Prediksi ini mengikuti hasil `PUT` yang sudah teruji dengan body lengkap; kombinasi persisnya tidak dijalankan.
    4. `{"judul": null}` ditolak `422` (`string_type`) karena `judul` bertipe `str` tanpa izin `None`. `{"judul": "x", "catatan": null}` diterima karena `catatan` bertipe `str | None`.

    Jawaban 1, 2, dan 4 diuji dengan `TestClient` dari FastAPI.

## Ringkasan

- Request body adalah data di dalam isi request, dipakai terutama dengan `POST`, `PUT`, `PATCH`, dan `DELETE`.
- Bentuk body dideklarasikan dengan model Pydantic: class turunan `BaseModel` dengan field bertipe.
- Parameter bertipe model dibaca sebagai body, parameter bertipe tunggal sebagai query, dan yang ada di path sebagai path parameter.
- Field tanpa default wajib; field dengan default atau `X | None = None` opsional.
- Body dikirim sebagai JSON dengan header `Content-Type: application/json`. Tanpa header itu, hasilnya `422`.
- Error `422` pada body memiliki `loc` yang diawali `body`. Field yang tidak dikenal diabaikan tanpa error.
- Bentuk body otomatis tercatat di dokumentasi.

## Langkah berikutnya

Kembali ke daftar materi di [Modul 03: Data dan Validasi](index.md). Materi berikutnya adalah model Pydantic.
