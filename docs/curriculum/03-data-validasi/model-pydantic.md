# Model Pydantic

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan apa itu model Pydantic dan mengapa FastAPI memakainya.
- [ ] Membuat model dengan berbagai jenis field: wajib, opsional, list, dan model bersarang.
- [ ] Membuat objek model dari argumen maupun dari `dict`, dan mengubahnya kembali menjadi `dict`.
- [ ] Menjelaskan aturan konversi tipe otomatis beserta batasannya.
- [ ] Membaca `ValidationError` dan lokasi kesalahan pada model bersarang.
- [ ] Memakai model bersarang dan daftar model sebagai request body.

## Prasyarat

- Sudah membaca [Request Body](request-body.md).
- Class dan type hints di Python, termasuk `list[str]` dan `X | None`.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, dan **Pydantic 2.14.1** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Di [Request Body](request-body.md) kamu sudah memakai `class TugasBaru(BaseModel)` tanpa membahasnya mendalam. Sekarang saatnya memahami apa yang sebenarnya terjadi.

**Pydantic** adalah library Python untuk memvalidasi data. Intinya sederhana: kamu mendeskripsikan **bentuk data** dalam sebuah class, lalu Pydantic memastikan data yang masuk sesuai bentuk itu. Class tersebut disebut **model**. Dalam dokumentasinya, model dibuat dengan mewarisi `BaseModel` dan mendefinisikan field sebagai atribut beranotasi tipe.

Mengapa ini penting di FastAPI?

| Tanpa model | Dengan model |
|---|---|
| Data masuk berupa `dict` mentah; kamu memeriksa sendiri tiap kunci dan tipenya | Pydantic memeriksa dan mengonversi otomatis |
| Salah ketik nama kunci baru ketahuan saat program jalan | Editor dapat mengenali nama field |
| Bentuk data hanya ada di kepala atau komentar | Bentuk data tercatat di dokumentasi otomatis |

Pydantic dipakai FastAPI untuk bagian data, seperti dijelaskan di [Apa itu FastAPI](../01-pengenalan/apa-itu-fastapi.md). Karena itu model bukan khusus FastAPI: kamu bisa memakainya di skrip Python biasa, dan itulah cara paling mudah untuk mempelajarinya.

## Bagian 1: model di Python biasa

### Kode model

Model-model ini dipakai di seluruh halaman. Simpan sebagai `models.py`:

```python title="models.py"
--8<-- "fastapi/03-data-validasi/model-pydantic/models.py"
```

| Bagian | Artinya |
|---|---|
| `class Alamat(BaseModel)` | Model untuk alamat |
| `kota: str` | Field **wajib** bertipe teks (tanpa nilai default) |
| `kode_pos: str \| None = None` | Field opsional: boleh teks atau tidak ada |
| `class Pengguna(BaseModel)` | Model untuk pengguna |
| `umur: int` | Field wajib bertipe bilangan bulat |
| `aktif: bool = True` | Field opsional dengan default `True` |
| `hobi: list[str] = []` | Field berupa daftar teks. Defaultnya daftar kosong |
| `alamat: Alamat \| None = None` | Field yang tipenya **model lain**. Inilah **model bersarang** (*nested model*) |

Soal `hobi: list[str] = []`: di fungsi Python biasa, default list yang bisa diubah itu jebakan karena dipakai bersama. Pada pengujian, dua objek `Pengguna` tidak berbagi daftar `hobi`: menambah item ke satu objek tidak memengaruhi objek lain. Jadi pola ini aman di Pydantic.

### Kode percobaan

Simpan sebagai `model_dasar.py` di folder yang sama:

```python title="model_dasar.py"
--8<-- "fastapi/03-data-validasi/model-pydantic/model_dasar.py"
```

### Penjelasan kode

| Bagian | Fungsinya |
|---|---|
| `Pengguna(nama="Budi", umur=25)` | Membuat objek model dari argumen. Jika data tidak valid, terjadi `ValidationError` |
| `budi.nama` | Field dibaca seperti atribut biasa |
| `budi.model_dump()` | Mengubah model menjadi `dict`. Model bersarang ikut diubah secara rekursif |
| `Pengguna.model_validate(data)` | Membuat dan memvalidasi model dari sebuah `dict`, termasuk `dict` bersarang |
| `Pengguna(nama="Rina", umur="28")` | Memberi `"28"` (teks) untuk field `int`. Dikonversi otomatis |
| `except ValidationError` | Menangkap kesalahan validasi. `galat.errors()` berisi daftar kesalahan |

### Menjalankan

```bash
python model_dasar.py
```

Hasil dari eksekusi nyata:

```text
nama='Budi' umur=25 aktif=True hobi=[] alamat=None
Budi 25 True
{'nama': 'Budi', 'umur': 25, 'aktif': True, 'hobi': [], 'alamat': None}
Makassar
28 int
('umur',) int_parsing Input should be a valid integer, unable to parse string as an integer
```

Baris pertama adalah tampilan objek model saat dicetak. Perhatikan bahwa field yang tidak diisi muncul dengan nilai default-nya. Pada model bersarang, `sari.alamat.kota` membaca lapisan kedua dengan rantai atribut.

## Aturan konversi tipe

Pydantic tidak kaku: ia berusaha **mengonversi** input agar cocok dengan tipe field. Dokumentasinya menyebut bahwa konversi ini bisa menyebabkan hilangnya informasi, dan bahwa ada *strict mode* untuk melarang konversi (strict mode tidak dibahas di sini). Hasil pengujian untuk field `umur: int`:

| Nilai yang diberikan | Hasil |
|---|---|
| `"30"` | `30` |
| `25.0` | `25` |
| `"25.0"` | `25` |
| `" 7 "` (dengan spasi) | `7` |
| `True` | `1` |
| `25.5` | Error `int_from_float` |
| `"tiga"` | Error `int_parsing` |
| `""` (teks kosong) | Error `int_parsing` |
| `"1e2"` | Error `int_parsing` |
| `None` | Error `int_type` |

Beberapa hal yang perlu diperhatikan:

- Nilai desimal hanya diterima jika sebenarnya bulat (`25.0`), dan ditolak jika ada pecahan (`25.5`), jadi informasi tidak diam-diam hilang.
- `True` diterima sebagai `1` untuk field `int`. Ini mungkin mengejutkan.
- Sebaliknya, field `str` **tidak** menerima angka: pada pengujian, `nama=5` ditolak dengan `string_type`.

Kesimpulannya: jangan menganggap konversi selalu terjadi. Tipe `str` ketat terhadap angka, sedangkan `int` cukup longgar terhadap teks angka.

## Bagian 2: model di FastAPI

Model yang sama dipakai sebagai request body. Simpan sebagai `main.py` di folder yang sama dengan `models.py`:

```python title="main.py"
--8<-- "fastapi/03-data-validasi/model-pydantic/main.py"
```

### Penjelasan kode

| Bagian | Fungsinya |
|---|---|
| `from models import Pengguna` | Mengimpor model dari file `models.py`. Model terpisah dari endpoint agar bisa dipakai ulang |
| `pengguna: Pengguna` | Parameter bertipe model dibaca sebagai body, seperti di [Request Body](request-body.md) |
| `pengguna.alamat.kota if pengguna.alamat else None` | `alamat` boleh `None`, jadi dicek dulu sebelum membaca `kota` |
| `daftar: list[Pengguna]` | Body berupa **daftar** pengguna: tipe teratas JSON adalah array |
| `[p.nama for p in daftar]` | Mengambil nama dari tiap model dalam daftar |

Menurut dokumentasi resmi FastAPI, model bersarang dapat dipakai dengan kedalaman bebas, dan list dari model juga dapat dijadikan body.

### Menjalankan

```bash
fastapi dev main.py
```

Pastikan terminal berada di folder yang berisi `main.py` dan `models.py`. Pada pengujian, `main.py` berhasil mengimpor `models` saat dijalankan dengan perintah ini dari folder tersebut.

## Mencoba request

Simpan body ke file lalu kirim dengan `-d "@file"`, seperti dijelaskan di [Request Body](request-body.md#mencoba-request). Contoh `pengguna.json`:

```json
{"nama":"Sari","umur":"30","aktif":false,"hobi":["membaca","menulis"],"alamat":{"kota":"Makassar","kode_pos":"90111"}}
```

```bash
curl -i -X POST "http://127.0.0.1:8000/pengguna" -H "Content-Type: application/json" -d "@pengguna.json"
```

Hasil nyata (`201 Created`): `umur` yang dikirim sebagai teks `"30"` sudah menjadi bilangan `30`.

```json
{"nama":"Sari","umur":30,"kota":"Makassar","data":{"nama":"Sari","umur":30,"aktif":false,"hobi":["membaca","menulis"],"alamat":{"kota":"Makassar","kode_pos":"90111"}}}
```

Hasil untuk body lain yang diuji:

| Body | Status | Hasil |
|---|---|---|
| `{"nama":"Budi","umur":25}` | `201` | `kota` `null`; `data` berisi nilai default (`aktif` `true`, `hobi` `[]`, `alamat` `null`) |
| `{"nama":"Rina","umur":28,"alamat":{"kota":"Gowa"}}` | `201` | `kota` `"Gowa"`; `kode_pos` di `data` bernilai `null` |
| Dua pengguna dalam array, ke `/pengguna/banyak` | `200` | `{"jumlah":2,"nama":["Gita","Hadi"]}` |

## Membaca error pada model bersarang

Pada model bersarang, bidang `loc` menunjuk ke lapisan yang salah. Hasil nyata:

| Body | `loc` | `type` |
|---|---|---|
| `{"nama":"Dedi","umur":"tiga"}` | `["body","umur"]` | `int_parsing` |
| `{"nama":"Eka","umur":20,"alamat":{"kode_pos":"90111"}}` | `["body","alamat","kota"]` | `missing` |
| `{"nama":"Fani","umur":20,"hobi":["membaca",5]}` | `["body","hobi",1]` | `string_type` |
| `{"nama":"Ina","umur":20,"alamat":"Makassar"}` | `["body","alamat"]` | `model_attributes_type` |
| Array dengan item ke-2 tanpa `nama` (`/pengguna/banyak`) | `["body",1,"nama"]` | `missing` |

Cara membaca `loc`: urutan lapisan dari luar ke dalam. Angka di dalamnya adalah **indeks** (mulai dari 0) dalam sebuah daftar. Jadi `["body","hobi",1]` berarti "item ke-2 dari `hobi`", dan `["body",1,"nama"]` berarti "field `nama` pada pengguna ke-2 dalam array".

Contoh body lengkap untuk kasus `alamat` tanpa `kota`:

```json
{"detail":[{"type":"missing","loc":["body","alamat","kota"],"msg":"Field required","input":{"kode_pos":"90111"}}]}
```

## Dokumentasi otomatis

Pada pengujian, `/openapi.json` mencatat dua skema, `Alamat` dan `Pengguna`. Field `alamat` pada `Pengguna` merujuk ke `Alamat` atau `null`. Field wajib `Pengguna` adalah `nama` dan `umur`, sedangkan `Alamat` hanya mewajibkan `kota`. Tampilan visualnya di Swagger UI belum saya periksa.

## Kesalahan umum

Semua kasus berikut dijalankan dan dicatat apa adanya.

### 1. Mengirim array ke endpoint yang mengharapkan satu objek

Mengirim array `[{"nama":"Gita","umur":21},{"nama":"Hadi","umur":22}]` ke `POST /pengguna` menghasilkan `422` dengan `loc` `["body"]` dan `type` `model_attributes_type`, sedangkan `input` berisi array yang dikirim. **Solusi:** kirim ke `/pengguna/banyak`, atau kirim satu objek.

### 2. Mengirim teks untuk field yang berupa model

`"alamat":"Makassar"` ditolak karena `alamat` harus berupa objek (`{"kota": ...}`), bukan teks. **Solusi:** ikuti bentuk bersarang yang didefinisikan model.

### 3. Mengira angka otomatis menjadi teks

`nama=5` ditolak (`string_type`). Konversi terjadi untuk teks menjadi angka, tetapi tidak sebaliknya.

### 4. Membaca field model bersarang yang bisa `None`

`pengguna.alamat.kota` akan error jika `alamat` bernilai `None`. Itulah mengapa `main.py` mengecek `if pengguna.alamat` lebih dulu. Skenario galat ini tidak saya jalankan sendiri; ia mengikuti perilaku umum Python untuk `None`.

### 5. Berasumsi field tak dikenal akan ditolak

Pada pengujian, `Pengguna(nama="x", umur=1, foo=1)` tidak menimbulkan error dan field `foo` tidak muncul di hasil `model_dump()`. Perilaku ini sama dengan yang terlihat di endpoint pada [Request Body](request-body.md).

## Latihan

1. **Dasar.** Buat model `Produk` dengan field `nama: str`, `harga: float`, dan `stok: int = 0`. Buat objeknya di Python biasa, lalu cetak `model_dump()`.
2. **Menengah.** Buat endpoint `POST /produk` yang menerima `Produk` dan mengembalikan `{"nama": ..., "nilai_stok": harga * stok}`. Uji dengan `{"nama":"Pensil","harga":2500.5,"stok":4}` dan dengan `harga` `"murah"`.
3. **Menengah.** Buat model `Item` (`nama: str`, `jumlah: int`) dan `Pesanan` (`pelanggan: str`, `item: list[Item]`). Buat `POST /pesanan` yang mengembalikan total `jumlah` semua item.
4. **Tantangan.** Tanpa menjalankan, prediksikan hasil `Pengguna(nama="x", umur=...)` untuk `umur` bernilai `25.0`, `25.5`, `"25"`, dan `True`. Lalu jalankan untuk memeriksa.

??? success "Kunci jawaban (sudah dijalankan)"
    1. Kode:

        ```python
        class Produk(BaseModel):
            nama: str
            harga: float
            stok: int = 0
        ```

    2. Kode:

        ```python
        @app.post("/produk")
        def produk(p: Produk):
            return {"nama": p.nama, "nilai_stok": p.harga * p.stok}
        ```

        Dengan `harga` 2500.5 dan `stok` 4 hasilnya `{"nama":"Pensil","nilai_stok":10002.0}`. Tanpa `stok`, `nilai_stok` bernilai `0.0`. Dengan `harga` `"murah"` hasilnya `422`, `type` `float_parsing`, `loc` `["body","harga"]`.
    3. Kode:

        ```python
        class Item(BaseModel):
            nama: str
            jumlah: int


        class Pesanan(BaseModel):
            pelanggan: str
            item: list[Item]


        @app.post("/pesanan")
        def pesanan(ps: Pesanan):
            return {"pelanggan": ps.pelanggan, "total_jumlah": sum(i.jumlah for i in ps.item)}
        ```

        Dengan dua item berjumlah 2 dan 3, hasilnya `{"pelanggan":"Budi","total_jumlah":5}`. Dengan `item` kosong (`[]`) hasilnya `total_jumlah` 0 (diterima, bukan error). Dengan `jumlah` `"banyak"` hasilnya `422` dengan `loc` `["body","item",0,"jumlah"]`.
    4. `25.0` menjadi `25`, `25.5` ditolak (`int_from_float`), `"25"` menjadi `25`, dan `True` menjadi `1` (lihat tabel konversi).

    Jawaban 2 dan 3 diuji dengan `TestClient` dari FastAPI.

## Ringkasan

- Model Pydantic adalah class turunan `BaseModel` yang mendeskripsikan bentuk data; Pydantic memvalidasi dan mengonversi data agar sesuai.
- Field tanpa default wajib; dengan default atau `X | None = None` opsional.
- Field dapat berupa tipe dasar, `list[...]`, atau model lain (model bersarang).
- `model_dump()` mengubah model menjadi `dict`, dan `model_validate()` membuat model dari `dict`.
- Konversi tipe otomatis ada batasnya: `"30"` menjadi `30`, `25.5` ditolak untuk `int`, dan angka tidak otomatis menjadi teks.
- Pada error, `loc` menunjukkan lapisan model bersarang dari luar ke dalam, dengan indeks untuk item dalam daftar.
- Model bersarang dan `list[Model]` dapat dipakai sebagai request body.

## Langkah berikutnya

Kembali ke daftar materi di [Modul 03: Data dan Validasi](index.md). Materi berikutnya adalah validasi field.
