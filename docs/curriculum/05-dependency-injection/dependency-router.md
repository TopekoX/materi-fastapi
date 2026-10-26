# Dependency per Router

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan apa itu `APIRouter` dan mengapa dependency bisa dipasang pada sekelompok endpoint sekaligus.
- [ ] Memasang dependency lewat `APIRouter(dependencies=[...])`.
- [ ] Memasang dependency saat `include_router(..., dependencies=[...])`.
- [ ] Memasang dependency untuk seluruh aplikasi lewat `FastAPI(dependencies=[...])`.
- [ ] Menyebutkan urutan eksekusi dependency global, router, dekorator, dan parameter.
- [ ] Menjelaskan bahwa hasil dependency router tidak diteruskan ke fungsi endpoint.

## Prasyarat

- Sudah membaca [Dependency Berantai](dependency-berantai.md) dan [Dependency Sederhana](dependency-sederhana.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7** dan **FastAPI 0.162.0** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Sampai sekarang kita memasang dependency satu per satu pada endpoint. Bayangkan sepuluh endpoint anggota yang semuanya mensyaratkan pengguna aktif. Menulis `Depends(pengguna_aktif)` sepuluh kali melelahkan, dan satu endpoint yang terlewat berarti satu lubang.

FastAPI menyediakan **`APIRouter`**: kelompok endpoint yang bisa diberi pengaturan bersama, yaitu `prefix`, `tags`, `responses`, dan `dependencies`. Menurut dokumentasi FastAPI, `APIRouter` bekerja seperti "FastAPI mini". Dependency yang dipasang pada router berlaku untuk **setiap** endpoint di dalamnya.

Ada tiga tingkat lingkup:

| Lingkup | Cara memasang | Berlaku untuk |
|---|---|---|
| Satu endpoint | `@router.get(..., dependencies=[...])` | endpoint itu saja |
| Satu router | `APIRouter(dependencies=[...])` atau `include_router(..., dependencies=[...])` | semua endpoint di router |
| Seluruh aplikasi | `FastAPI(dependencies=[...])` | semua endpoint |

Halaman ini memakai satu file supaya fokus pada dependency. Memecah router ke banyak file adalah topik [Modul 08](../08-struktur-proyek/index.md).

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/05-dependency-injection/dependency-router/main.py"
```

## Penjelasan kode

### Rantai dari halaman sebelumnya

`pengguna_saat_ini`, `pengguna_aktif`, dan `pengelola` sama seperti di [Dependency Berantai](dependency-berantai.md). Bedanya, masing-masing memanggil fungsi `catat`, yang menulis namanya ke `request.state.jejak`. Ini hanya alat percobaan agar urutan eksekusi terlihat; `request.state` menyimpan data selama satu request.

!!! warning "Bukan autentikasi sungguhan"
    Pengguna ditentukan dari header `X-Pengguna` buatan sendiri, hanya untuk contoh. Autentikasi yang aman dibahas di Modul 07.

### Tiga router

```python
router_publik = APIRouter(prefix="/publik", tags=["publik"])

router_anggota = APIRouter(
    prefix="/anggota",
    tags=["anggota"],
    dependencies=[Depends(pengguna_aktif)],
)

router_admin = APIRouter(prefix="/admin", tags=["admin"])
```

- `prefix` ditambahkan di depan setiap path di router. Endpoint `"/profil"` di `router_anggota` menjadi `/anggota/profil`. `prefix` tidak boleh diakhiri `/`.
- `tags` mengelompokkan endpoint di dokumentasi.
- `router_publik` tidak punya dependency: terbuka untuk siapa saja.
- `router_anggota` memasang `pengguna_aktif` sejak awal.
- `router_admin` dibuat polos; dependency-nya ditambahkan saat dimasukkan ke aplikasi.

### Endpoint

```python
@router_anggota.get("/profil")
def profil(pengguna: Annotated[dict, Depends(pengguna_saat_ini)]):
    return pengguna
```

Memakai `@router_anggota.get(...)`, bukan `@app.get(...)`. Endpoint ini tidak mendeklarasikan `pengguna_aktif`, tetapi tetap dilindungi karena dependency router. Dokumentasi FastAPI menyatakan hasil dependency router tidak diteruskan ke fungsi endpoint, seperti dependency pada dekorator. Karena itu `profil` mendeklarasikan `pengguna_saat_ini` lagi untuk mendapatkan datanya.

```python
@router_anggota.get("/urutan", dependencies=[Depends(dependensi_dekorator)])
def urutan(request: Request, _: Annotated[None, Depends(dependensi_parameter)]):
    return {"jejak": request.state.jejak}
```

Endpoint ini memakai ketiga bentuk sekaligus: dependency router (`pengguna_aktif`), dependency dekorator, dan dependency parameter. Responsnya menampilkan urutan eksekusi.

### Memasang dependency saat `include_router`

```python
app = FastAPI(dependencies=[Depends(dependensi_global)])
app.include_router(router_publik)
app.include_router(router_anggota)
app.include_router(router_admin, dependencies=[Depends(pengelola)])
```

- `FastAPI(dependencies=[...])` adalah dependency **global**: berlaku untuk semua endpoint.
- `include_router` memasukkan router ke aplikasi. Parameter `dependencies` di sini berlaku untuk semua endpoint router itu, tanpa mengubah routernya. Menurut dokumentasi FastAPI, router yang sama dapat dipakai ulang di proyek lain dengan pengaturan berbeda.
- `router_admin` kini mensyaratkan `pengelola`, yang di dalam rantainya sudah memuat `pengguna_aktif` dan `pengguna_saat_ini`.

## Menjalankan

```powershell
fastapi dev main.py
```

Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah.

## Mencoba request

Hasil di bawah dijalankan dengan `curl.exe` (`-i` menampilkan baris status, `-H` menambah header).

### Router publik: tanpa syarat

```powershell
curl.exe -i http://127.0.0.1:8000/publik/info
```

```text
HTTP/1.1 200 OK
{"nama":"Perpustakaan","terbuka":true}
```

### Router anggota: dilindungi dependency router

| Request | Status | Isi |
|---|---|---|
| `GET /anggota/profil`, `X-Pengguna: budi` | `200` | `{"nama":"budi","peran":"anggota","aktif":true}` |
| `GET /anggota/profil`, `X-Pengguna: sari` | `403` | `{"detail":"Akun tidak aktif"}` |
| `GET /anggota/profil`, `X-Pengguna: hantu` | `401` | `{"detail":"Pengguna tidak dikenal"}` |
| `GET /anggota/profil`, tanpa header | `422` | dua entri `missing` dengan `loc` `["header","x-pengguna"]` |

Baris terakhir menunjukkan sesuatu yang perlu diketahui: karena `x-pengguna` dibutuhkan lewat dua jalur (dependency router dan dependency parameter pada `profil`), kesalahan yang sama dilaporkan dua kali. Itu hasil pengamatan; saya tidak menelusuri penyebabnya lebih jauh.

### Router admin: dependency dari `include_router`

| Request | Status | Isi |
|---|---|---|
| `GET /admin/laporan`, `X-Pengguna: rina` | `200` | `{"pesan":"Laporan khusus pengelola"}` |
| `GET /admin/laporan`, `X-Pengguna: budi` | `403` | `{"detail":"Hanya untuk pengelola"}` |
| `GET /admin/laporan`, `X-Pengguna: sari` | `403` | `{"detail":"Akun tidak aktif"}` |
| `GET /admin/laporan`, `X-Pengguna: hantu` | `401` (`TestClient`) | `{"detail":"Pengguna tidak dikenal"}` |

Endpoint `laporan` tidak punya satu pun baris `Depends`, tetapi tetap dijaga.

### Urutan eksekusi

```powershell
curl.exe -H "X-Pengguna: budi" http://127.0.0.1:8000/anggota/urutan
```

```json
{"jejak":["global","pengguna_saat_ini","pengguna_aktif","dekorator","parameter"]}
```

Urutan yang teramati: dependency **global**, lalu dependency **router** (dengan rantainya), lalu dependency **dekorator**, lalu dependency **parameter**. Dokumentasi FastAPI menyatakan urutan router, dekorator, lalu parameter; urutan global terhadap router tidak dinyatakan di sana, jadi posisi `global` di atas adalah hasil pengamatan pada versi ini.

### Dokumentasi otomatis

`/openapi.json` mencatat `tags` sesuai router (`publik`, `anggota`, `admin`), dan header `x-pengguna` sebagai parameter pada endpoint `/anggota/*` dan `/admin/laporan`. `/publik/info` tidak punya parameter. Tampilan Swagger UI **belum diverifikasi** lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Mengira nilai dependency router tersedia di fungsi endpoint | Tidak. Deklarasikan dependency lagi sebagai parameter bila datanya dibutuhkan (seperti `profil`). |
| Menaruh endpoint yang seharusnya publik di router yang dilindungi | Ikut dijaga. Pisahkan ke router lain, seperti `router_publik`. |
| Lupa memasukkan router dengan `include_router` | Endpoint di router tidak ada di aplikasi. |
| Memasang dependency yang sama di router dan di endpoint tanpa alasan | Kerja berulang dan kemungkinan kesalahan validasi tercatat ganda (lihat baris tanpa header di atas). |
| Mengandalkan urutan antara dependency global dan router | Dokumentasi tidak menjamin urutan itu; ia teramati pada versi ini saja. |
| Menambah route ke `router` setelah di-`include` | Dokumentasi FastAPI menyarankan menambah route lewat dekorator sebelum memasukkan router. |

## Latihan

1. **Dasar.** Tambahkan `GET /anggota/pinjaman` ke `router_anggota`. Apakah ia otomatis dilindungi? Apa status untuk `sari`, `budi`, dan tanpa header?
2. **Prediksi.** Apa status `GET /admin/laporan` untuk `hantu`? Tingkat rantai mana yang menolak?
3. **Pilih lingkup.** Kamu ingin semua endpoint mencatat log akses. Di mana dependency sebaiknya dipasang: endpoint, router, atau aplikasi?
4. **Analisis.** Mengapa `profil` masih mendeklarasikan `Depends(pengguna_saat_ini)` padahal router sudah memasang `pengguna_aktif`?

??? success "Kunci jawaban"
    Jawaban 1 dan 2 dijalankan dengan `TestClient`. Jawaban 3 dan 4 adalah penalaran dari penjelasan di atas dan dokumentasi FastAPI.

    ```python
    @router_anggota.get("/pinjaman")
    def pinjaman():
        return {"pinjaman": []}
    ```

    (ditambahkan sebelum router dimasukkan ke aplikasi)

    1. Ya, otomatis dilindungi: `sari` mendapat `403` (`Akun tidak aktif`), `budi` mendapat `200` (`{"pinjaman":[]}`), dan tanpa header mendapat `422` (`missing`).
    2. `401` dengan `{"detail":"Pengguna tidak dikenal"}`, ditolak oleh `pengguna_saat_ini`, tingkat paling awal rantai.
    3. Di aplikasi: `FastAPI(dependencies=[Depends(...)])`, karena berlaku untuk semua endpoint.
    4. Karena hasil dependency router tidak diteruskan ke fungsi endpoint. Endpoint perlu mendeklarasikan dependency lagi bila membutuhkan datanya.

## Ringkasan

- `APIRouter` mengelompokkan endpoint dengan `prefix`, `tags`, dan `dependencies` bersama.
- Dependency bisa dipasang di endpoint (dekorator), router (`APIRouter(...)` atau `include_router(...)`), atau aplikasi (`FastAPI(dependencies=[...])`).
- Hasil dependency router tidak diteruskan ke endpoint; deklarasikan lagi bila datanya dibutuhkan.
- Urutan yang dinyatakan dokumentasi: router, lalu dekorator, lalu parameter. Pada versi yang diuji, dependency global teramati berjalan paling awal.
- Pisahkan endpoint publik dan terlindungi ke router berbeda agar syarat tidak bocor.

## Langkah berikutnya

Kembali ke daftar materi di [Modul 05: Dependency Injection](index.md). Dengan ini seluruh materi Modul 05 selesai. Modul berikutnya adalah [Modul 06: Basis Data](../06-basis-data/index.md).
