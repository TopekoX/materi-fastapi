# Query Parameter

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan apa itu query parameter dan membedakannya dari path parameter.
- [ ] Membuat query parameter wajib, ber-default, dan opsional.
- [ ] Membaca dan menulis URL yang memuat query dengan benar.
- [ ] Menjelaskan bagaimana FastAPI mengonversi tipe, termasuk `bool`, dan menolak nilai yang tidak valid.
- [ ] Menggabungkan path parameter dan query parameter dalam satu endpoint.

## Prasyarat

- Sudah membaca [Path Parameter](path-parameter.md).
- Type hints dasar di Python, termasuk nilai default argumen fungsi.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7** dan **FastAPI 0.162.0** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Path parameter mengidentifikasi **sumber daya mana** yang diminta, misalnya tugas nomor 3. Tetapi sering kita juga ingin menambahkan **opsi** pada permintaan: "tampilkan hanya tugas yang sudah selesai" atau "batasi hasil menjadi 2 saja". Untuk itu dipakai **query parameter**.

Query parameter ditulis di akhir URL setelah tanda tanya `?`. Setiap pasangan berbentuk `nama=nilai`, dan pasangan dipisahkan tanda `&`:

```text
/tugas?selesai=true&batas=2
       │└─────────┘ └─────┘
       │  pasangan 1  pasangan 2
       └── awal query
```

Perbandingan singkat dengan path parameter:

| | Path parameter | Query parameter |
|---|---|---|
| Letak di URL | Bagian dari path: `/tugas/3` | Setelah `?`: `/tugas?batas=2` |
| Cara mendeklarasikan | Kurung kurawal di path | Argumen fungsi yang tidak ada di path |
| Umumnya dipakai untuk | Menunjuk satu sumber daya | Opsi: filter, batas, pencarian |
| Wajib? | Selalu wajib | Tergantung ada tidaknya nilai default |

Dokumentasi resmi FastAPI menyebutkan aturan intinya: argumen fungsi yang tidak termasuk path parameter otomatis dianggap sebagai query parameter.

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/02-dasar-routing/query-parameter/main.py"
```

## Penjelasan kode

### Data contoh

```python
DAFTAR_TUGAS = [
    {"id": 1, "judul": "Belajar FastAPI", "selesai": True},
    ...
]
```

Sebuah list berisi empat tugas, disimpan di memori sebagai pengganti basis data. Data ini hanya untuk contoh. Penyimpanan sungguhan dibahas di Modul 06.

### Query parameter dengan nilai default

```python
@app.get("/tugas")
def daftar_tugas(selesai: bool | None = None, batas: int = 10):
```

Path `/tugas` tidak punya kurung kurawal, jadi kedua argumen fungsi menjadi query parameter.

| Argumen | Artinya |
|---|---|
| `batas: int = 10` | Query parameter bertipe bilangan bulat dengan **default** `10`. Karena punya default, parameter ini **tidak wajib**. Jika tidak dikirim, nilainya `10` |
| `selesai: bool \| None = None` | Query parameter **opsional**. Tipe `bool \| None` berarti nilainya boleh `True`, `False`, atau tidak ada (`None`). Default `None` menandakan "filter tidak dipakai". Penulisan `X \| None` memakai sintaks Python 3.10 ke atas, seperti pada dokumentasi resmi |

### Memakai nilainya

```python
    hasil = DAFTAR_TUGAS
    if selesai is not None:
        hasil = [t for t in hasil if t["selesai"] == selesai]
    hasil = hasil[:batas]
    return {"jumlah": len(hasil), "data": hasil}
```

| Baris | Fungsinya |
|---|---|
| `if selesai is not None:` | Filter hanya dijalankan jika klien mengirim `selesai`. Dibandingkan dengan `None`, bukan `if selesai:`, agar nilai `False` tetap dianggap filter yang sah |
| `[t for t in hasil if ...]` | *List comprehension*: menyaring tugas yang nilai `selesai`-nya cocok |
| `hasil[:batas]` | Mengambil paling banyak `batas` item pertama |

### Query parameter wajib

```python
@app.get("/cari")
def cari(kata: str):
```

Argumen `kata` **tidak punya default**, sehingga menjadi query parameter yang **wajib**. Request tanpa `kata` akan ditolak.

### Hubungan antarbagian

```text
Request  : GET /tugas?selesai=true&batas=1
              │  FastAPI memisahkan path dan query
              ▼
Path     : /tugas  → cocok dengan daftar_tugas
Query    : selesai="true" → True (bool),  batas="1" → 1 (int)
              ▼
Fungsi   : daftar_tugas(selesai=True, batas=1)
              ▼
Response : {"jumlah":1,"data":[...]}
```

## Menjalankan aplikasi

```bash
fastapi dev main.py
```

Contoh di bawah memakai port `8000`; sesuaikan bila berbeda. Cara menjalankan server dijelaskan di [Menjalankan Server](../01-pengenalan/menjalankan-server.md).

## Mencoba request

!!! warning "Apit URL dengan tanda kutip"
    Tanda `&` memiliki arti khusus di banyak shell. Di PowerShell misalnya, `&` adalah operator pemanggil. Biasakan mengapit URL yang memuat query dengan tanda kutip, seperti pada contoh berikut. Pengguna PowerShell mengetik `curl.exe`.

```bash
curl -i "http://127.0.0.1:8000/tugas"
curl -i "http://127.0.0.1:8000/tugas?batas=2"
curl -i "http://127.0.0.1:8000/tugas?selesai=true"
curl -i "http://127.0.0.1:8000/cari?kata=fastapi"
```

Hasil dari eksekusi nyata (isi `data` diringkas jadi nomor tugas):

| Request | Status | Hasil |
|---|---|---|
| `GET /tugas` | `200 OK` | `jumlah` 4, tugas 1 sampai 4 (default `batas=10`) |
| `GET /tugas?batas=2` | `200 OK` | `jumlah` 2, tugas 1 dan 2 |
| `GET /tugas?selesai=true` | `200 OK` | `jumlah` 2, tugas 1 dan 2 |
| `GET /tugas?selesai=false` | `200 OK` | `jumlah` 2, tugas 3 dan 4 |
| `GET /tugas?selesai=true&batas=1` | `200 OK` | `jumlah` 1, tugas 1 |
| `GET /cari?kata=fastapi` | `200 OK` | `{"kata":"fastapi","hasil":[...tugas 1...]}` |
| `GET /cari?kata=Belajar%20FastAPI` | `200 OK` | `kata` `"Belajar FastAPI"`, tugas 1 |
| `GET /cari?kata=zzz` | `200 OK` | `{"kata":"zzz","hasil":[]}` |

Contoh body lengkap untuk `GET /tugas?batas=2`:

```json
{"jumlah":2,"data":[{"id":1,"judul":"Belajar FastAPI","selesai":true},{"id":2,"judul":"Membuat endpoint pertama","selesai":true}]}
```

Beberapa hal yang bisa diamati:

- `GET /tugas` tanpa query tetap berhasil, karena kedua parameternya punya default.
- Urutan pasangan dalam query tidak penting. Query dikenali berdasarkan namanya.
- Query yang tidak dikenal diabaikan: `GET /tugas?foo=1` menghasilkan `200` dengan hasil yang sama seperti tanpa query.
- Spasi ditulis `%20` pada URL dan dikembalikan menjadi spasi oleh FastAPI, seperti pada path parameter.

## Konversi dan validasi

Nilai di URL selalu berupa teks. Tipe pada argumen membuat FastAPI mengonversinya dan menolak nilai yang tidak valid, sama seperti pada [Path Parameter](path-parameter.md#konversi-dan-validasi).

### Aturan `bool`

Dokumentasi resmi menyebut nilai seperti `1`, `true`, `on`, dan `yes` sebagai `True`, serta `0`, `false`, `off`, dan `no` sebagai `False`. Hasil pengujian pada parameter `selesai`:

| Nilai di URL | Hasil |
|---|---|
| `true` | `200`, dibaca `True` |
| `false` | `200`, dibaca `False` |
| `yes` | `200`, dibaca `True` |
| `1` | `200`, dibaca `True` |
| `ya` | `422`, `bool_parsing` |
| `maybe` | `422`, `bool_parsing` |
| (kosong) `?selesai=` | `422`, `bool_parsing` |

Perhatikan bahwa `ya` (bahasa Indonesia) **tidak dikenali**. Gunakan `true` atau `false`.

### Nilai bukan angka

`GET /tugas?batas=abc` mengembalikan `422`:

```json
{"detail":[{"type":"int_parsing","loc":["query","batas"],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"abc"}]}
```

Bedanya dengan error path parameter ada di bidang `loc`: sekarang isinya `["query","batas"]`, bukan `["path", ...]`. Bidang ini memberi tahu di bagian URL mana kesalahannya.

### Parameter wajib yang tidak dikirim

`GET /cari` tanpa `kata` mengembalikan `422`:

```json
{"detail":[{"type":"missing","loc":["query","kata"],"msg":"Field required","input":null}]}
```

Jenis kesalahannya `missing` dan `input` bernilai `null`, karena memang tidak ada nilai yang dikirim.

## Dokumentasi otomatis

Pada pengujian, `/openapi.json` mencatat parameter `batas` dengan `in: query`, `required: false`, tipe `integer`, dan default `10`. Parameter `selesai` bertipe `boolean` atau `null` dan tidak wajib. Parameter `kata` pada `/cari` bertipe `string` dan **wajib** (`required: true`). Jadi sifat wajib atau tidaknya terbaca langsung dari kode, tanpa kamu menulis dokumentasi.

## Menggabungkan path dan query parameter

FastAPI membedakan keduanya berdasarkan nama: argumen yang ada di path menjadi path parameter, sisanya menjadi query parameter. Urutan penulisan argumen tidak berpengaruh.

```python
@app.get("/pengguna/{pengguna_id}/tugas")
def tugas_pengguna(pengguna_id: int, selesai: bool = False, batas: int = 10):
    return {"pengguna_id": pengguna_id, "selesai": selesai, "batas": batas}
```

Pada pengujian:

| Request | Hasil |
|---|---|
| `GET /pengguna/7/tugas` | `{"pengguna_id":7,"selesai":false,"batas":10}` |
| `GET /pengguna/7/tugas?selesai=true&batas=3` | `{"pengguna_id":7,"selesai":true,"batas":3}` |
| `GET /pengguna/x/tugas?batas=abc` | `422` dengan **dua** error: `["path","pengguna_id"]` dan `["query","batas"]` |

Perhatikan baris terakhir: ketika dua nilai sekaligus tidak valid, kedua kesalahan dilaporkan dalam satu response.

## Kesalahan umum

Semua kasus berikut dijalankan dan dicatat apa adanya.

### 1. Parameter wajib terlupa (`422`)

`GET /cari` mengembalikan `422` dengan `type` `missing`. **Solusi:** kirim parameternya (`/cari?kata=...`), atau beri default jika memang boleh kosong.

### 2. Nilai `bool` yang tidak dikenali (`422`)

`?selesai=ya` ditolak. **Solusi:** pakai `true`/`false`, `1`/`0`, `yes`/`no`, atau `on`/`off`.

### 3. Salah ketik nama query: diabaikan tanpa peringatan

`GET /tugas?foo=1` tetap `200`. Jika kamu salah mengetik `?selsai=true` (huruf tertukar), FastAPI tidak memberi tahu: parameter itu dianggap tidak dikenal dan filter tidak dipakai. Karena itu, jika hasil tidak sesuai harapan, periksa ejaan nama parameter terlebih dahulu. Kasus `selsai` itu sendiri tidak saya jalankan; perilakunya sama dengan `foo` yang teruji.

### 4. Nilai yang masuk akal secara tipe, tetapi tidak masuk akal secara makna

`GET /tugas?batas=-1` mengembalikan `200` dengan **tiga** tugas, bukan error atau nol tugas. Penyebabnya bukan FastAPI: `-1` valid sebagai bilangan bulat, lalu `hasil[:-1]` pada Python berarti "semua kecuali yang terakhir". Validasi tipe tidak mengecek makna. Pembatasan seperti "minimal 0" memakai fitur validasi tambahan yang dibahas di [Modul 03](../03-data-validasi/index.md). `batas=0` menghasilkan `jumlah` 0 dan daftar kosong.

### 5. Nama yang sama dikirim dua kali

`GET /tugas?batas=1&batas=3` menghasilkan `jumlah` 3, jadi nilai terakhir (`3`) yang dipakai untuk parameter bertipe `int`. Cara menerima banyak nilai sekaligus tidak dibahas di sini dan belum saya uji.

## Latihan

1. **Dasar.** Tambahkan endpoint `GET /sapa` dengan query parameter `nama: str = "teman"` yang mengembalikan `{"pesan": "Halo, <nama>!"}`. Panggil `/sapa` dan `/sapa?nama=Budi`.
2. **Menengah.** Tambahkan query parameter `mulai: int = 0` pada `/tugas` agar hasil diambil dengan `hasil[mulai:mulai + batas]`. Prediksikan lalu uji `/tugas?mulai=2&batas=1`.
3. **Menengah.** Prediksikan nomor tugas yang muncul untuk `/tugas?selesai=false&batas=1`, lalu uji.
4. **Tantangan.** Ubah `/cari` agar `kata` menjadi opsional (default `None`), dan tampilkan semua tugas jika `kata` tidak dikirim.

??? success "Kunci jawaban (sudah dijalankan)"
    1. Kode:

        ```python
        @app.get("/sapa")
        def sapa(nama: str = "teman"):
            return {"pesan": f"Halo, {nama}!"}
        ```

        `/sapa` menghasilkan `{"pesan":"Halo, teman!"}`, dan `/sapa?nama=Budi` menghasilkan `{"pesan":"Halo, Budi!"}`.
    2. Tugas nomor 3 (`jumlah` 1). Tugas yang dilewati adalah nomor 1 dan 2.
    3. Tugas nomor 3. Dari tugas yang belum selesai (3 dan 4), diambil satu yang pertama.
    4. Kode:

        ```python
        @app.get("/cari")
        def cari(kata: str | None = None):
            hasil = DAFTAR_TUGAS
            if kata:
                hasil = [t for t in hasil if kata.lower() in t["judul"].lower()]
            return {"ids": [t["id"] for t in hasil]}
        ```

        `/cari` menghasilkan semua nomor `[1,2,3,4]`, dan `/cari?kata=latihan` menghasilkan `[4]`.

    Jawaban diuji dengan `TestClient` dari FastAPI, bukan lewat `curl`.

## Ringkasan

- Query parameter ditulis setelah `?`, berbentuk `nama=nilai`, dan dipisah `&`. Cocok untuk opsi seperti filter dan batas.
- Argumen fungsi yang tidak ada di path otomatis menjadi query parameter.
- Tanpa default → wajib. Dengan default → opsional. Default `None` dengan tipe `X | None` → boleh tidak ada.
- Tipe pada argumen membuat FastAPI mengonversi dan memvalidasi nilai. Nilai tidak valid menghasilkan `422`, dengan `loc` yang menunjukkan bagian `query`.
- Nilai `bool` yang dikenali antara lain `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off`. Nilai `ya` ditolak.
- Query yang tidak dikenal diabaikan tanpa peringatan, dan validasi tipe tidak memeriksa makna nilainya.
- Path dan query parameter bisa digabung dalam satu endpoint. Keduanya dibedakan lewat nama.

## Langkah berikutnya

Kembali ke daftar materi di [Modul 02: Dasar Routing](index.md). Materi berikutnya adalah urutan route.
