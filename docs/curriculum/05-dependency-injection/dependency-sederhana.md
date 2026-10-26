# Dependency Sederhana

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Membuat dependency fungsi yang mengambil data atau menolak request dengan `HTTPException`.
- [ ] Membuat dependency berupa class dan memakainya dengan `Depends()`.
- [ ] Memakai `dependencies=[...]` pada dekorator untuk dependency yang hanya memeriksa.
- [ ] Menjelaskan perbedaan dependency yang nilainya dipakai dan yang tidak.
- [ ] Membaca dari mana parameter dependency berasal lewat `loc` pada error `422`.
- [ ] Menulis dependency `def` maupun `async def`.

## Prasyarat

- Sudah membaca [Konsep Dependency](konsep-dependency.md).
- Sudah membaca [HTTPException](../04-penanganan-error/http-exception.md).
- Dasar `class` di Python (`__init__` dan atribut).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7** dan **FastAPI 0.162.0** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Di halaman sebelumnya, dependency berupa fungsi yang mengembalikan `dict`. Itu bentuk paling sederhana. Halaman ini menunjukkan tiga bentuk sederhana lain yang paling sering kamu temui:

| Bentuk | Dipakai ketika | Contoh di halaman ini |
|---|---|---|
| Fungsi yang **mengambil data atau menolak** request | Beberapa endpoint perlu langkah awal yang sama, misalnya "cari data atau jawab `404`" | `ambil_buku` |
| **Class** | Kamu ingin mengelompokkan nilai dalam objek dengan atribut, bukan `dict` | `Paginasi` |
| Dependency **yang hanya memeriksa** | Hasilnya tidak dibutuhkan endpoint, hanya efek "lolos atau ditolak" | `wajib_klien` |

Menurut dokumentasi FastAPI, dependency harus berupa sesuatu yang bisa dipanggil (*callable*). Fungsi bisa dipanggil, begitu juga class: membuat objek dari class berarti memanggil class tersebut.

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/05-dependency-injection/dependency-sederhana/main.py"
```

## Penjelasan kode

### 1. Dependency yang mengambil data atau menolak

```python
def ambil_buku(buku_id: Annotated[int, Path(ge=1)]) -> dict:
    if buku_id not in buku_db:
        raise HTTPException(status_code=404, detail=f"Buku {buku_id} tidak ditemukan")
    return buku_db[buku_id]


BukuDitemukan = Annotated[dict, Depends(ambil_buku)]
```

- Dependency menerima `buku_id` dari path, sebab nama parameternya sama dengan bagian `{buku_id}` di path endpoint.
- Bila buku tidak ada, dependency me-`raise` `HTTPException`. Request berhenti di sini, dan fungsi endpoint tidak pernah dijalankan.
- Bila ada, buku dikembalikan dan diterima endpoint sebagai argumen.
- Dengan begitu `lihat_buku`, `hapus_buku`, dan `pinjam_buku` tidak perlu mengulang pemeriksaan "ada atau tidak".

```python
@app.get("/buku/{buku_id}")
def lihat_buku(buku: BukuDitemukan):
    return buku
```

Fungsi endpoint tidak punya parameter `buku_id`; yang ia terima langsung data bukunya.

### 2. Dependency berupa class

```python
class Paginasi:
    def __init__(
        self,
        halaman: Annotated[int, Query(ge=1)] = 1,
        batas: Annotated[int, Query(ge=1, le=50)] = 2,
    ):
        self.halaman = halaman
        self.batas = batas
        self.awal = (halaman - 1) * batas
```

Parameter `__init__` (selain `self`) dibaca FastAPI seperti parameter fungsi: itulah query parameter-nya. FastAPI membuat objek `Paginasi` dari nilai request dan menyerahkannya ke endpoint.

```python
@app.get("/buku")
def daftar_buku(paginasi: Annotated[Paginasi, Depends()]):
    semua = list(buku_db.values())
    hasil = semua[paginasi.awal : paginasi.awal + paginasi.batas]
```

`Depends()` tanpa argumen adalah jalan pintas: FastAPI memakai tipe yang dideklarasikan (`Paginasi`) sebagai dependency. Menurut dokumentasi FastAPI, bentuk lengkapnya `Annotated[Paginasi, Depends(Paginasi)]` sama saja. Keuntungan class dibanding `dict`: editor dapat melengkapi `paginasi.awal` dan memeriksa salah ketik atribut.

### 3. Dependency yang hanya memeriksa

```python
def wajib_klien(x_klien: Annotated[str, Header()]) -> None:
    if x_klien not in KLIEN_DIIZINKAN:
        raise HTTPException(status_code=400, detail="Header X-Klien tidak dikenal")
```

Dependency ini tidak mengembalikan apa-apa; ia hanya menolak bila header `X-Klien` tidak dikenal. Nilainya tidak dibutuhkan endpoint, jadi dipasang di dekorator:

```python
@app.post("/buku/{buku_id}/pinjam", dependencies=[Depends(wajib_klien)])
def pinjam_buku(buku: BukuDitemukan):
```

`dependencies` menerima daftar `Depends(...)`. Dependency tetap dijalankan, tetapi hasilnya tidak diteruskan ke fungsi endpoint (dokumentasi FastAPI). `Header` bekerja seperti `Query`, tetapi membaca header request. FastAPI mengubah `x_klien` menjadi nama header `x-klien`.

!!! warning "Bukan keamanan sungguhan"
    Header `X-Klien` di sini hanya contoh. Memeriksa header buatan sendiri tidak aman untuk autentikasi; dokumentasi FastAPI menyarankan perangkat keamanan terpadu. Ini dibahas di Modul 07.

### `def` atau `async def`

Dependency boleh ditulis `def` biasa atau `async def`, dan boleh dicampur dengan endpoint jenis apa pun (dokumentasi FastAPI). Gunakan `async def` bila dependency memakai `await`, misalnya menunggu layanan luar. Contohnya ada di `main_async.py`:

```python title="main_async.py"
--8<-- "fastapi/05-dependency-injection/dependency-sederhana/main_async.py"
```

`ambil_cuaca` adalah `async def` (dengan `await asyncio.sleep(...)` sebagai pengganti menunggu layanan luar), sedangkan `ambil_zona_waktu` adalah `def` biasa. Keduanya dipakai oleh endpoint `def` (`/info`) dan endpoint `async def` (`/info-async`). Pengantar async/await ada di [Dasar Async/Await](../02-dasar-routing/async-await.md).

Jalankan dengan `fastapi dev main_async.py`. Hasil `curl` untuk `/info` dan `/info-async` sama:

```json
{"cuaca":{"kota":"Bandung","suhu":24},"zona":"WIB"}
```

Keempat kombinasi (dependency `async`/`def` dengan endpoint `async`/`def`) berhasil pada contoh ini, tetapi tidak diukur kinerjanya.

## Menjalankan

```powershell
fastapi dev main.py
```

Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah.

## Mencoba request

Hasil di bawah dijalankan berurutan dengan `curl.exe` dari keadaan awal server (`-i` menampilkan baris status).

### Class `Paginasi`

| Request | Status | Isi |
|---|---|---|
| `GET /buku` | `200` | `{"halaman":1,"batas":2,"data":[` buku 1 dan 2 `]}` |
| `GET /buku?halaman=2` | `200` | `data` berisi buku 3 dan 4 |
| `GET /buku?halaman=0` | `422` | `loc` `["query","halaman"]`, `greater_than_equal` |

Contoh respons lengkap `GET /buku`:

```json
{"halaman":1,"batas":2,"data":[{"id":1,"judul":"Dasar Python","dipinjam":false},{"id":2,"judul":"Belajar FastAPI","dipinjam":true}]}
```

### Dependency `ambil_buku`

| Request | Status | Isi |
|---|---|---|
| `GET /buku/1` | `200` | `{"id":1,"judul":"Dasar Python","dipinjam":false}` |
| `GET /buku/99` | `404` | `{"detail":"Buku 99 tidak ditemukan"}` |
| `GET /buku/0` | `422` | `loc` `["path","buku_id"]`, `greater_than_equal` |
| `DELETE /buku/3` | `204` | tanpa isi |
| `DELETE /buku/3` (ulang) | `404` | `{"detail":"Buku 3 tidak ditemukan"}` |

Satu dependency yang sama melayani `GET` dan `DELETE`.

### Dependency pemeriksa

```powershell
curl.exe -i -X POST http://127.0.0.1:8000/buku/1/pinjam -H "X-Klien: web"
```

```text
HTTP/1.1 200 OK
{"id":1,"judul":"Dasar Python","dipinjam":true}
```

| Request | Status | Isi |
|---|---|---|
| `POST /buku/1/pinjam` tanpa header | `422` | `loc` `["header","x-klien"]`, `missing` |
| `POST /buku/1/pinjam`, `X-Klien: robot` | `400` | `{"detail":"Header X-Klien tidak dikenal"}` |
| `POST /buku/1/pinjam`, `X-Klien: web` | `200` | buku dengan `"dipinjam":true` |
| `POST /buku/1/pinjam` (ulang) | `409` | `{"detail":"Buku sedang dipinjam"}` |
| `POST /buku/99/pinjam` tanpa header | `404` | `{"detail":"Buku 99 tidak ditemukan"}` |

Baris terakhir menarik: walau header `X-Klien` tidak dikirim, hasilnya `404`, bukan `422`. Teramati pada pengujian ini bahwa `ambil_buku` sudah menolak request sebelum kesalahan header dilaporkan. Jangan menggantungkan urutan antar pemeriksaan tanpa mengujinya.

### Dokumentasi otomatis

`/openapi.json` mencatat `halaman` dan `batas` (query) untuk `GET /buku`, serta `buku_id` (path) dan `x-klien` (header) untuk `POST /buku/{buku_id}/pinjam`. Parameter dari dependency tetap muncul walau tidak ada di fungsi endpoint. Tampilan Swagger UI **belum diverifikasi** lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Menaruh `buku_id` di endpoint dan dependency sekaligus | Dideklarasikan dua kali; cukup di dependency. |
| Mengira `dependencies=[...]` meneruskan hasilnya ke endpoint | Tidak. Hasilnya dibuang (dokumentasi FastAPI). Bila nilai dibutuhkan, pakai parameter biasa dengan `Depends`. |
| Memakai `Depends(Paginasi())` | Sama dengan kesalahan memakai kurung pada fungsi: yang diserahkan adalah objek, bukan callable. Pakai `Depends()` atau `Depends(Paginasi)`. |
| Mengira class dependency perlu didaftarkan di tempat lain | Tidak. Cukup sebagai callable dengan parameter `__init__`. |
| Memakai header buatan sendiri sebagai pengaman | Tidak aman. Gunakan alat keamanan resmi (Modul 07). |
| Mengandalkan urutan pemeriksaan antar dependency | Urutan error yang teramati tidak selalu seperti dugaan (lihat baris `404` di atas). |

## Latihan

1. **Class.** Buat class `Pencarian` dengan query `q` (opsional, minimal 2 karakter) dan `urut` (default `"judul"`). Pasang dengan `Depends()` pada `GET /cari`. Apa hasil `GET /cari?q=p`?
2. **Dependency yang mengembalikan nilai.** Ubah `wajib_klien` agar mengembalikan nama klien, lalu pakai sebagai parameter endpoint `GET /siapa`.
3. **Prediksi.** Pada `main.py`, apa status `POST /buku/99/pinjam` tanpa header? Mengapa bukan `422`?
4. **Analisis.** Kapan sebaiknya memakai `dependencies=[...]` di dekorator, dan kapan parameter biasa dengan `Depends`?

??? success "Kunci jawaban"
    Jawaban 1 dan 2 dijalankan dengan `TestClient`. Jawaban 3 dari hasil `curl` di atas. Jawaban 4 adalah penalaran dari dokumentasi FastAPI.

    ```python
    from typing import Annotated
    from fastapi import Depends, FastAPI, Header, HTTPException, Query

    app = FastAPI()


    class Pencarian:
        def __init__(
            self,
            q: Annotated[str | None, Query(min_length=2)] = None,
            urut: str = "judul",
        ):
            self.q = q
            self.urut = urut


    @app.get("/cari")
    def cari(p: Annotated[Pencarian, Depends()]):
        return {"q": p.q, "urut": p.urut}


    def klien(x_klien: Annotated[str, Header()]) -> str:
        if x_klien not in {"web", "mobile"}:
            raise HTTPException(400, "Header X-Klien tidak dikenal")
        return x_klien


    @app.get("/siapa")
    def siapa(k: Annotated[str, Depends(klien)]):
        return {"klien": k}
    ```

    1. `GET /cari` menghasilkan `{"q":null,"urut":"judul"}`; `GET /cari?q=py&urut=tahun` menghasilkan `{"q":"py","urut":"tahun"}`; `GET /cari?q=p` menghasilkan `422` `string_too_short` dengan `loc` `["query","q"]`.
    2. Dengan header `X-Klien: mobile`: `{"klien":"mobile"}`. Dengan nilai lain: `400` `Header X-Klien tidak dikenal`.
    3. `404`. Pada pengujian, `ambil_buku` menolak request lebih dulu sehingga kesalahan header tidak dilaporkan.
    4. `dependencies=[...]` bila hanya efek periksa yang dibutuhkan dan nilainya tidak dipakai, supaya fungsi endpoint tidak punya parameter yang tidak terpakai. Parameter biasa dengan `Depends` bila endpoint membutuhkan nilainya.

## Ringkasan

- Dependency bisa berupa fungsi atau class; keduanya hanya perlu bisa dipanggil.
- Dependency fungsi cocok untuk langkah awal bersama, termasuk "ambil data atau jawab `404`" lewat `HTTPException`.
- Dependency class membungkus nilai dalam objek berantribut; `Annotated[Kelas, Depends()]` adalah jalan pintasnya.
- `dependencies=[Depends(...)]` pada dekorator menjalankan dependency tanpa meneruskan hasilnya.
- Parameter dependency (query, path, header) tampil di dokumentasi otomatis dan divalidasi seperti parameter endpoint.

## Langkah berikutnya

Kembali ke daftar materi di [Modul 05: Dependency Injection](index.md). Materi berikutnya adalah dependency berantai: dependency yang bergantung pada dependency lain.
