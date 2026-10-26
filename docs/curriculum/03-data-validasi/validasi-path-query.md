# Validasi Path dan Query Parameter

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menambahkan batasan nilai pada path parameter dengan `Path`.
- [ ] Menambahkan batasan panjang, rentang, dan pola pada query parameter dengan `Query`.
- [ ] Menulis `Annotated` dengan benar dan membedakan parameter wajib dari opsional.
- [ ] Menerima beberapa nilai untuk satu query parameter (`list`) dan memakai `alias`.
- [ ] Membaca response `422` untuk parameter (`loc` berawalan `path` atau `query`).

## Prasyarat

- Sudah membaca [Path Parameter](../02-dasar-routing/path-parameter.md) dan [Query Parameter](../02-dasar-routing/query-parameter.md).
- Sudah membaca [Validasi Field](validasi-field.md). Argumen `ge`, `le`, `min_length`, dan `pattern` di halaman ini sama artinya dengan di `Field`.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7** dan **FastAPI 0.162.0** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Di Modul 02 kamu sudah memakai parameter bertipe: `buku_id: int` menolak `"abc"`. Tetapi `buku_id` bernilai `-3` atau `0` tetap lolos, begitu juga `batas=100000` untuk jumlah data per halaman.

FastAPI menyediakan dua fungsi untuk menambah aturan:

| Fungsi | Dipakai untuk |
|---|---|
| `Path(...)` | Path parameter, misalnya `/buku/{buku_id}` |
| `Query(...)` | Query parameter, misalnya `?halaman=2` |

Keduanya diimpor dari `fastapi`. Argumen validasinya sama dengan `Field` di Pydantic:

| Argumen | Arti | Untuk tipe |
|---|---|---|
| `gt` / `ge` | lebih besar dari / lebih besar atau sama dengan | angka |
| `lt` / `le` | lebih kecil dari / lebih kecil atau sama dengan | angka |
| `min_length` / `max_length` | panjang minimum / maksimum | teks; `max_length` juga untuk `list` |
| `pattern` | harus cocok dengan *regular expression* | teks |

Aturan dipasang lewat `Annotated`, yaitu fitur type hints Python untuk menempelkan metadata pada sebuah tipe. Bentuknya:

```python
nama: Annotated[TipeData, Query(aturan...)] = nilai_default
```

Tipe ada di dalam `Annotated`, sedangkan nilai default tetap ditulis di luar, setelah tanda `=`. Dokumentasi FastAPI menganjurkan gaya `Annotated` ini.

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/03-data-validasi/validasi-path-query/main.py"
```

## Penjelasan kode

### Impor

```python
from typing import Annotated

from fastapi import FastAPI, Path, Query
```

`Annotated` berasal dari modul `typing` bawaan Python. `Path` dan `Query` dari FastAPI.

### Path parameter dengan batas nilai

```python
buku_id: Annotated[int, Path(title="ID buku", ge=1, le=9999)],
```

- `int` adalah tipe, jadi `"abc"` ditolak.
- `ge=1, le=9999` membatasi nilai antara 1 dan 9999.
- `title` hanya metadata untuk dokumentasi otomatis, bukan aturan validasi.

Path parameter **selalu wajib** karena menjadi bagian URL. Karena itu `Path` tidak diberi nilai default.

### Query parameter berpola

```python
tampilan: Annotated[str, Query(pattern="^(ringkas|lengkap)$")] = "ringkas",
```

Nilainya hanya boleh `ringkas` atau `lengkap`. Tanda `|` berarti "atau", `^` awal teks, dan `$` akhir teks. Karena ada `= "ringkas"` di luar `Annotated`, parameter ini opsional.

### Query parameter opsional dengan batas panjang

```python
cari: Annotated[
    str | None,
    Query(min_length=2, max_length=30, description="Kata kunci judul"),
] = None,
```

`str | None` berarti nilainya teks atau `None`. `= None` membuatnya opsional. Aturan panjang hanya diperiksa bila parameter dikirim.

### Batas angka dan `list`

```python
halaman: Annotated[int, Query(ge=1)] = 1,
batas: Annotated[int, Query(ge=1, le=50)] = 10,
tag: Annotated[list[str] | None, Query(max_length=3)] = None,
```

`halaman` minimal 1, `batas` antara 1 dan 50. Untuk `tag`, `Query` **wajib** ditulis agar FastAPI membaca `list` dari query string (`?tag=a&tag=b`); tanpa itu, FastAPI menganggap `list` sebagai request body (menurut dokumentasi FastAPI; tidak dijalankan di sini). `max_length=3` pada `list` berarti paling banyak 3 item.

### Alias

```python
urut_berdasarkan: Annotated[str, Query(alias="urut-berdasarkan")] = "judul",
```

Tanda hubung tidak boleh ada di nama variabel Python, jadi nama di URL (`urut-berdasarkan`) dipisah dari nama variabel (`urut_berdasarkan`) lewat `alias`. Setelah ada alias, URL **harus** memakai nama alias.

### Parameter wajib

```python
def laporan(tahun: Annotated[int, Query(ge=2000, le=2100)]):
```

Tanpa nilai default, parameter wajib. Jika tidak dikirim, hasilnya `422` dengan `type` `missing`. Perhatikan: menulis `str | None` saja **tidak** membuat parameter opsional. Yang membuatnya opsional adalah `= None`.

## Menjalankan

Siapkan venv seperti di [Instalasi dan Virtual Environment](../01-pengenalan/instalasi-dan-venv.md), lalu:

```powershell
fastapi dev main.py
```

Server berjalan di `http://127.0.0.1:8000`. Dokumentasi interaktif ada di `/docs`.

## Mencoba request

Contoh berikut dijalankan dengan `curl.exe` (PowerShell). URL diberi tanda kutip karena memuat `?` dan `&`.

### Nilai valid

```powershell
curl.exe "http://127.0.0.1:8000/buku/5?tampilan=lengkap"
```

```json
{"buku_id":5,"tampilan":"lengkap"}
```

### Path melanggar batas

```powershell
curl.exe -i "http://127.0.0.1:8000/buku/0"
```

Baris status: `HTTP/1.1 422 Unprocessable Content`. Isi response (hasil uji dengan `TestClient`):

```json
{"detail": [{"type": "greater_than_equal", "loc": ["path", "buku_id"], "msg": "Input should be greater than or equal to 1", "input": "0", "ctx": {"ge": 1}}]}
```

Perhatikan `loc`: `["path", "buku_id"]` menunjukkan error ada di path parameter. Untuk query parameter, awalnya `"query"`.

### Query melanggar aturan

```powershell
curl.exe "http://127.0.0.1:8000/buku/5?tampilan=xyz"
```

```json
{"detail":[{"type":"string_pattern_mismatch","loc":["query","tampilan"],"msg":"String should match pattern '^(ringkas|lengkap)$'","input":"xyz","ctx":{"pattern":"^(ringkas|lengkap)$"}}]}
```

### Beberapa pelanggaran sekaligus

```powershell
curl.exe "http://127.0.0.1:8000/buku?cari=a&batas=99"
```

```json
{"detail":[{"type":"string_too_short","loc":["query","cari"],"msg":"String should have at least 2 characters","input":"a","ctx":{"min_length":2}},{"type":"less_than_equal","loc":["query","batas"],"msg":"Input should be less than or equal to 50","input":"99","ctx":{"le":50}}]}
```

### Hasil pengujian lain

Diuji dengan `TestClient` (bukan lewat `curl`):

| Request | Status | Keterangan |
|---|---|---|
| `/buku` | 200 | semua default: `halaman` 1, `batas` 10, `tag` `null`, `urut_berdasarkan` `"judul"` |
| `/buku?batas=50` | 200 | tepat di batas atas diterima |
| `/buku?batas=51` | 422 | `less_than_equal` |
| `/buku?halaman=0` | 422 | `greater_than_equal` |
| `/buku?tag=a&tag=b` | 200 | `"tag": ["a", "b"]` |
| `/buku?tag=a&tag=b&tag=c&tag=d` | 422 | `too_long` |
| `/buku/abc` | 422 | `int_parsing` (kesalahan tipe, bukan aturan) |
| `/buku?urut-berdasarkan=tahun` | 200 | `"urut_berdasarkan": "tahun"` |
| `/buku?urut_berdasarkan=tahun` | 200 | nama variabel diabaikan: nilainya tetap `"judul"` |
| `/laporan` | 422 | `missing` |
| `/laporan?tahun=1999` | 422 | `greater_than_equal` |

### Dokumentasi otomatis

`/openapi.json` memuat aturan tersebut: `minimum`/`maximum` pada `buku_id`, `pattern` pada `tampilan`, `minLength`/`maxLength` dan `description` pada `cari`, `maxItems` pada `tag`, serta nama `urut-berdasarkan` pada parameter. Tampilan visual di Swagger UI **belum diverifikasi** lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Lupa `Query()` pada `list` | Menurut dokumentasi FastAPI, `list` dianggap request body. Tidak dijalankan di sini. |
| Mengira `str \| None` membuat parameter opsional | Tanpa `= None`, parameter tetap wajib (dokumentasi FastAPI). |
| Memakai nama variabel, bukan alias, di URL | Diabaikan: `?urut_berdasarkan=tahun` tetap memakai default (teruji di atas). |
| Memberi default pada `Path` | Path parameter selalu wajib; dokumentasi menyatakan parameter `Path` tidak boleh punya default. |
| Menulis default di dalam `Query(default=...)` sekaligus `= nilai` di luar | Ambigu; dokumentasi menganjurkan default di luar `Annotated`. Tidak dijalankan di sini. |
| Memakai `ge`/`le` pada teks | `ge`/`le` untuk angka. Untuk teks pakai `min_length`, `max_length`, atau `pattern`. |

## Latihan

1. **Dasar.** Buat endpoint `GET /halaman/{nomor}` dengan `nomor` bilangan bulat lebih besar dari 0. Apa `type` error untuk `/halaman/0`?
2. **Desimal.** Buat `GET /harga` dengan query `maks` bertipe `float`, lebih besar dari 0 dan kurang dari 1.000.000. Apakah `0.5` diterima? Apakah `0`?
3. **Wajib.** Buat `GET /cari` dengan query `q` wajib, minimal 3 karakter. Apa yang terjadi bila `q` tidak dikirim, dan bila `q=ab`?
4. **Alias dan pola.** Buat `GET /kode` dengan query berpola `^BK\d{3}$` yang dikirim sebagai `kode-buku` dan berdefault `"BK001"`. Uji `BK12`, `BK123`, dan tanpa parameter.

??? success "Kunci jawaban"
    Semua jawaban dijalankan dengan `TestClient`, bukan lewat browser.

    ```python
    from typing import Annotated
    from fastapi import FastAPI, Path, Query

    app = FastAPI()


    @app.get("/halaman/{nomor}")
    def halaman(nomor: Annotated[int, Path(gt=0)]):
        return {"nomor": nomor}


    @app.get("/harga")
    def harga(maks: Annotated[float, Query(gt=0, lt=1000000)]):
        return {"maks": maks}


    @app.get("/cari")
    def cari(q: Annotated[str, Query(min_length=3)]):
        return {"q": q}


    @app.get("/kode")
    def kode(
        kode: Annotated[str, Query(alias="kode-buku", pattern=r"^BK\d{3}$")] = "BK001",
    ):
        return {"kode": kode}
    ```

    1. `/halaman/0` menghasilkan `422` dengan `type` `greater_than` (bukan `greater_than_equal`) dan `loc` `["path", "nomor"]`. `/halaman/1` menghasilkan `200`.
    2. `maks=0.5` diterima (`200`). `maks=0` ditolak (`greater_than`). `maks=1000000` juga ditolak (`less_than`), karena memakai `lt`.
    3. Tanpa `q`: `422` dengan `type` `missing`. `q=ab`: `422` dengan `string_too_short`. `q=abc`: `200`.
    4. `kode-buku=BK12`: `422` `string_pattern_mismatch`, dengan `loc` `["query", "kode-buku"]` (nama alias). `kode-buku=BK123`: `200`. Tanpa parameter: `200` dengan `"kode": "BK001"`.

## Ringkasan

- `Path` dan `Query` menambah aturan pada path dan query parameter; argumennya sama dengan `Field`.
- Pasang aturan lewat `Annotated[Tipe, Query(...)]`; default tetap di luar, setelah `=`.
- Angka: `gt`, `ge`, `lt`, `le`. Teks: `min_length`, `max_length`, `pattern`. `list`: `max_length` membatasi jumlah item.
- `list` di query string wajib memakai `Query()`.
- Tanpa default berarti wajib; `str | None` saja tidak membuatnya opsional. Path parameter selalu wajib.
- `alias` memisahkan nama di URL dari nama variabel.
- Pelanggaran menghasilkan `422`; `loc` diawali `path` atau `query`.

## Langkah berikutnya

Kembali ke daftar materi di [Modul 03: Data dan Validasi](index.md). Materi berikutnya adalah response model, yaitu mengatur bentuk data yang dikembalikan.
