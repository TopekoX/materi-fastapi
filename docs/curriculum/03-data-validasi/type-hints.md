# Type Hints untuk FastAPI

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan apa itu type hints dan bahwa Python sendiri tidak memaksakannya.
- [ ] Menulis tipe dasar, `list[...]`, `dict[...]`, dan `X | None`.
- [ ] Memakai `Literal` untuk membatasi nilai pada pilihan tertentu.
- [ ] Membaca dan menulis `Annotated`.
- [ ] Menjelaskan bagaimana FastAPI memakai type hints untuk validasi, konversi, dan dokumentasi.

## Prasyarat

- Selesai [Modul 02: Dasar Routing](../02-dasar-routing/index.md).
- Dasar Python: fungsi, `list`, dan `dict`.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, dan **Pydantic 2.14.1** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**. Penulisan `X | None` dan `list[str]` seperti di halaman ini adalah sintaks Python modern; kamu mungkin menemui `Optional[X]` dan `List[str]` di kode lama.

## Konsep

**Type hint** (petunjuk tipe) adalah catatan pada kode yang menyatakan tipe data suatu variabel, parameter, atau nilai kembalian. Contoh: `nama: str` berarti `nama` seharusnya teks.

Sejak Modul 01 kamu sudah memakainya, misalnya `buku_id: int`. Di FastAPI, type hints bukan sekadar catatan. Menurut dokumentasi FastAPI, tipe yang kamu tulis dipakai untuk:

- mendefinisikan kebutuhan parameter (path, query, body),
- **mengonversi** data request ke tipe yang dideklarasikan,
- **memvalidasi** data dan mengirim error otomatis bila tidak cocok,
- **mendokumentasikan** API lewat OpenAPI,
- memberi bantuan editor, misalnya autocompletion.

Karena itu, memahami type hints berarti memahami cara berbicara dengan FastAPI.

## Type hints di Python biasa

Simpan sebagai `dasar_type_hints.py`. Ini skrip Python biasa, tanpa FastAPI:

```python title="dasar_type_hints.py"
--8<-- "fastapi/03-data-validasi/type-hints/dasar_type_hints.py"
```

Jalankan:

```powershell
python dasar_type_hints.py
```

Hasil:

```text
Halo Budi, umur bukan angka
6
tamu Sari
{'nama': <class 'str'>, 'umur': <class 'int'>, 'return': <class 'str'>}
(<class 'str'>, 'metadata apa saja')
('rendah', 'tinggi')
```

### Penjelasan

- **Baris 1:** `sapa("Budi", "bukan angka")` tetap jalan walau `umur` dideklarasikan `int`. **Python tidak memaksakan type hints.** Yang memaksakannya adalah alat lain, seperti FastAPI.
- **`get_type_hints(sapa)`:** type hints tersimpan sebagai data yang bisa dibaca program lain. Itulah yang dimanfaatkan FastAPI saat aplikasi dimulai.
- **`get_args(Pesan)`:** `Annotated` menyimpan tipe asli (`str`) dan metadata tambahan. Python sendiri tidak memakai metadata itu; alat seperti FastAPI yang membacanya.

### Daftar tipe yang akan sering kamu pakai

| Penulisan | Artinya |
|---|---|
| `str`, `int`, `float`, `bool` | tipe dasar |
| `list[int]` | `list` yang setiap isinya `int` |
| `dict[str, float]` | `dict` dengan kunci `str` dan nilai `float` |
| `tuple[int, int, str]`, `set[bytes]` | `tuple` tiga isi dan `set` berisi `bytes` |
| `str \| None` | teks atau `None` (boleh kosong) |
| `int \| str` | salah satu dari dua tipe |
| `Literal["a", "b"]` | hanya boleh tepat `"a"` atau `"b"` |
| `Annotated[str, ...]` | tipe `str` plus metadata untuk alat lain |
| `NamaKelas` | objek dari kelas itu, termasuk model Pydantic |

`Optional[str]` di kode lama artinya sama dengan `str | None` (dokumentasi FastAPI). Materi ini memakai `str | None`.

## Type hints di FastAPI

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/03-data-validasi/type-hints/main.py"
```

### Penjelasan kode

```python
def hitung(angka: int, kali: float = 1.0):
```

`angka` berasal dari path dan harus `int`; `kali` dari query dan harus `float`. Nilai default membuat `kali` opsional.

```python
class Pesanan(BaseModel):
    produk: str
    jumlah: int
    prioritas: Literal["rendah", "normal", "tinggi"] = "normal"
    tag: list[str] = []
    catatan: str | None = None
```

Model Pydantic memakai type hints yang sama. `Literal` membatasi `prioritas` pada tiga pilihan, `list[str]` mensyaratkan daftar teks, dan `str | None = None` membuat `catatan` opsional.

```python
kata: Annotated[str | None, Query(min_length=2)] = None,
urut: Literal["judul", "tahun"] = "judul",
label: Annotated[list[str] | None, Query()] = None,
```

- `Annotated[str | None, Query(min_length=2)]`: tipenya `str | None`, dan `Query(...)` adalah metadata yang dibaca FastAPI (lihat [Validasi Path dan Query Parameter](validasi-path-query.md)).
- `Literal` juga bisa dipakai pada query parameter.
- `label` memakai `Query()` agar `list` dibaca dari query string.

## Menjalankan

```powershell
fastapi dev main.py
```

## Mencoba request

Hasil di bawah dijalankan dengan `curl.exe` ke server `fastapi dev`.

### Konversi tipe

```powershell
curl.exe "http://127.0.0.1:8000/hitung/4?kali=2.5"
```

```json
{"hasil":10.0}
```

`"4"` dari URL dikonversi menjadi `int` dan `"2.5"` menjadi `float` sebelum dihitung.

### Tipe salah

```powershell
curl.exe "http://127.0.0.1:8000/hitung/empat"
```

```json
{"detail":[{"type":"int_parsing","loc":["path","angka"],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"empat"}]}
```

### `Literal` dan `list` di query

Hasil `label=["a","b"]` di bawah diuji dengan `TestClient`; response `literal_error` berasal dari `curl`.

```powershell
curl.exe "http://127.0.0.1:8000/cari?urut=tahun&label=a&label=b"
```

```json
{"kata":null,"urut":"tahun","label":["a","b"]}
```

```powershell
curl.exe "http://127.0.0.1:8000/cari?urut=abjad"
```

```json
{"detail":[{"type":"literal_error","loc":["query","urut"],"msg":"Input should be 'judul' or 'tahun'","input":"abjad","ctx":{"expected":"'judul' or 'tahun'"}}]}
```

### Model dengan tipe campuran

Dengan body `{"produk":"Buku","jumlah":"3","prioritas":"tinggi","tag":["a","b"]}` (disimpan sebagai `pesanan.json`):

```powershell
curl.exe -X POST http://127.0.0.1:8000/pesanan -H "Content-Type: application/json" -d "@pesanan.json"
```

```json
{"produk":"Buku","jumlah":3,"prioritas":"tinggi","tag":["a","b"],"catatan":null}
```

`"3"` dikonversi menjadi `3`. Dengan body yang salah semuanya (`jumlah` berupa `"banyak"`, `prioritas` berupa `"darurat"`, `tag` berupa `"a"`), ketiga pelanggaran dilaporkan sekaligus:

```json
{"detail":[{"type":"int_parsing","loc":["body","jumlah"],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"banyak"},{"type":"literal_error","loc":["body","prioritas"],"msg":"Input should be 'rendah', 'normal' or 'tinggi'","input":"darurat","ctx":{"expected":"'rendah', 'normal' or 'tinggi'"}},{"type":"list_type","loc":["body","tag"],"msg":"Input should be a valid list","input":"a"}]}
```

### Dokumentasi otomatis

`/openapi.json` mengubah `Literal` menjadi daftar pilihan, misalnya `{"type": "string", "enum": ["rendah", "normal", "tinggi"], "default": "normal"}` untuk `prioritas`. Tampilan visual Swagger UI **belum diverifikasi** lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Mengira Python menolak tipe yang salah | Tidak. Python menjalankan kode tetap (lihat `sapa("Budi", "bukan angka")`). FastAPI dan Pydantic yang memvalidasi. |
| Menulis `list[str] \| None = None` untuk query parameter tanpa `Query()` | Nilai dari query string tidak terbaca; hasil uji: `{"label":null}` untuk `?label=a&label=b`. Pakai `Annotated[list[str] \| None, Query()]`. |
| Mengira `str \| None` membuat parameter opsional | Opsional karena ada `= None`. Tanpa default, parameter tetap wajib (dokumentasi FastAPI). |
| Menulis `List[str]` dan `Optional[str]` tanpa tahu artinya | Itu gaya lama untuk `list[str]` dan `str \| None`; artinya sama. |
| Mengira `Literal` mengubah huruf besar-kecil | `Literal` mencocokkan nilai persis; `"Tinggi"` bukan `"tinggi"`. Perilaku ini tidak dijalankan di sini. |

## Latihan

1. **Dasar.** Tulis type hints untuk: fungsi yang menerima daftar angka dan mengembalikan jumlahnya; fungsi dengan parameter `nama` teks yang boleh kosong.
2. **`Literal`.** Buat `GET /status/{nama}` yang hanya menerima `aktif` atau `nonaktif`. Apa `type` error untuk `ghoib`?
3. **Opsional.** Buat `GET /skor` dengan `skor: int | None = None` dan `bonus: float = 0`. Apa hasil `/skor`, `/skor?skor=7&bonus=1.5`, dan `/skor?skor=x`?
4. **`list`.** Buat `GET /ids` yang wajib menerima daftar `int` dari query. Uji `ids=1&ids=2`, `ids=1&ids=a`, dan tanpa parameter.

??? success "Kunci jawaban"
    Jawaban 2 sampai 4 dijalankan dengan `TestClient`. Jawaban 1 tidak dijalankan.

    ```python
    from typing import Annotated, Literal
    from fastapi import FastAPI, Query

    app = FastAPI()


    def jumlah(angka: list[int]) -> int: ...
    def sapa(nama: str | None = None) -> str: ...


    @app.get("/status/{nama}")
    def status(nama: Literal["aktif", "nonaktif"]):
        return {"nama": nama}


    @app.get("/skor")
    def skor(skor: int | None = None, bonus: float = 0):
        return {"skor": skor, "bonus": bonus}


    @app.get("/ids")
    def ids(ids: Annotated[list[int], Query()]):
        return {"ids": ids}
    ```

    1. `list[int]` untuk daftar angka dengan nilai kembalian `int`, dan `str | None` (dengan `= None`) untuk teks yang boleh kosong.
    2. `ghoib` menghasilkan `422` dengan `type` `literal_error` dan `loc` `["path","nama"]`. `aktif` menghasilkan `200`.
    3. `/skor` → `{"skor":null,"bonus":0}` (nilai default tidak dikonversi, jadi `bonus` tetap `0`, bukan `0.0`). `/skor?skor=7&bonus=1.5` → `{"skor":7,"bonus":1.5}`. `/skor?skor=x` → `422` `int_parsing`.
    4. `ids=1&ids=2` → `{"ids":[1,2]}`. `ids=1&ids=a` → `422` `int_parsing` dengan `loc` `["query","ids",1]` (indeks item yang salah). Tanpa parameter → `422` `missing`.

## Ringkasan

- Type hints menyatakan tipe data; Python sendiri tidak memaksakannya.
- FastAPI membaca type hints untuk memvalidasi, mengonversi, dan mendokumentasikan data.
- `list[int]`, `dict[str, float]`, dan `X | None` adalah bentuk yang paling sering dipakai.
- `Literal` membatasi nilai pada pilihan tertentu, dan tampil sebagai `enum` di dokumentasi.
- `Annotated[Tipe, metadata]` menyimpan tipe asli plus metadata yang dibaca FastAPI, misalnya `Query(...)`.
- Opsional ditentukan oleh `= nilai_default`, bukan oleh `| None` saja.

## Langkah berikutnya

Lanjut ke [Request Body](request-body.md), atau kembali ke daftar materi di [Modul 03: Data dan Validasi](index.md).
