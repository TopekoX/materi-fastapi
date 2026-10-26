# HTTPException

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan fungsi `HTTPException` dan mengapa ia di-`raise`, bukan di-`return`.
- [ ] Mengembalikan `404`, `400`, dan `409` dengan pesan yang jelas.
- [ ] Memakai `detail` berupa teks maupun objek JSON.
- [ ] Menambahkan header khusus pada response error.
- [ ] Memindahkan pemeriksaan "data ada atau tidak" ke fungsi pembantu agar tidak berulang.
- [ ] Memahami urutan: validasi parameter dijalankan sebelum kode fungsi.
- [ ] Mendokumentasikan error buatan sendiri di `/docs` dengan `responses`.

## Prasyarat

- Sudah membaca [Status Code](status-code.md).
- Selesai [Modul 03: Data dan Validasi](../03-data-validasi/index.md). Proyek tahap 1 di sana sudah memakai `HTTPException` secara singkat; halaman ini membahasnya dengan lengkap.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7** dan **FastAPI 0.162.0** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Sampai sekarang, kegagalan yang terjadi di API kita datang dari FastAPI sendiri (`422` untuk validasi). Tetapi banyak kegagalan hanya bisa diketahui oleh **kode kita**: buku tidak ada di penyimpanan, buku sedang dipinjam, lama peminjaman terlalu panjang. Untuk itu FastAPI menyediakan `HTTPException`.

`HTTPException` adalah *exception* biasa Python, yaitu objek yang menghentikan jalannya fungsi ketika di-`raise`. Saat FastAPI menerimanya, ia menjawab klien dengan status code dan `detail` yang kamu tentukan, lalu eksekusi fungsi berhenti di titik itu.

!!! warning "`raise`, bukan `return`"
    `HTTPException` harus di-**raise**. Bila kamu `return`, ia diperlakukan sebagai data biasa. Hasil uji ada di bagian [Kesalahan umum](#kesalahan-umum).

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/04-penanganan-error/http-exception/main.py"
```

## Penjelasan kode

### Fungsi pembantu dengan `404`

```python
def ambil_buku(buku_id: int) -> dict:
    if buku_id not in buku_db:
        raise HTTPException(
            status_code=404,
            detail=f"Buku dengan id {buku_id} tidak ditemukan",
            headers={"X-Kesalahan": "buku-tidak-ada"},
        )
    return buku_db[buku_id]
```

- `status_code` adalah status response. Pilih berdasarkan tabel di [Status Code](status-code.md).
- `detail` adalah pesan untuk klien. Di sini berupa teks.
- `headers` menambahkan header ke response error. Menurut dokumentasi FastAPI, ini jarang dibutuhkan; dipakai di sini hanya untuk contoh.
- Karena `raise` terjadi di dalam fungsi pembantu, fungsi endpoint yang memanggilnya ikut berhenti. Menurut dokumentasi FastAPI, ini berlaku untuk fungsi pembantu yang dipanggil dari endpoint. Dengan begitu pemeriksaan "ada atau tidak" cukup ditulis sekali.

### `400` untuk permintaan yang tidak masuk akal

```python
if hari > 14:
    raise HTTPException(status_code=400, detail="Lama peminjaman maksimal 14 hari")
```

Nilai `hari` sudah lolos validasi tipe dan `ge=1`, tetapi aturan "maksimal 14 hari" adalah aturan bisnis. Kita menegakkannya di kode dan menjawab `400`.

### `409` dengan `detail` berupa objek

```python
if not buku["tersedia"]:
    raise HTTPException(
        status_code=409,
        detail={"kode": "BUKU_DIPINJAM", "pesan": "Buku sedang dipinjam"},
    )
```

`409 Conflict` cocok ketika request bertabrakan dengan keadaan data saat ini. Menurut dokumentasi FastAPI, `detail` boleh berupa nilai apa pun yang bisa diubah menjadi JSON, seperti `dict` atau `list`. Objek memudahkan klien membaca kode kesalahan tanpa mengurai teks.

### Urutan pemeriksaan di endpoint

```python
buku = ambil_buku(buku_id)      # 1. ada tidaknya buku (404)
if hari > 14: ...               # 2. aturan lama pinjam (400)
if not buku["tersedia"]: ...    # 3. keadaan buku (409)
buku["tersedia"] = False        # 4. baru ubah data
```

Pemeriksaan yang menolak ditaruh di depan, dan perubahan data di akhir. Dengan begitu data tidak berubah bila ada error.

!!! note "Sebelum kode fungsi"
    Validasi parameter (`ge=1`, tipe `int`) dijalankan FastAPI **sebelum** fungsi dipanggil. Bila gagal, jawabannya `422` dan fungsi tidak dijalankan sama sekali.

## Menjalankan

```powershell
fastapi dev main.py
```

Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah.

## Mencoba request

Hasil di bawah dijalankan berurutan dengan `curl.exe` dari keadaan awal server. Opsi `-i` menampilkan baris status dan header.

### Sukses

```powershell
curl.exe -i http://127.0.0.1:8000/buku/1
```

```text
HTTP/1.1 200 OK
{"judul":"Dasar Python","tersedia":true}
```

### `404` dengan header khusus

```powershell
curl.exe -i http://127.0.0.1:8000/buku/99
```

```text
HTTP/1.1 404 Not Found
x-kesalahan: buku-tidak-ada
content-type: application/json
{"detail":"Buku dengan id 99 tidak ditemukan"}
```

### `400`, `409`, dan sukses meminjam

| Request | Status | Isi |
|---|---|---|
| `POST /buku/1/pinjam?hari=20` | `400 Bad Request` | `{"detail":"Lama peminjaman maksimal 14 hari"}` |
| `POST /buku/2/pinjam` | `409 Conflict` | `{"detail":{"kode":"BUKU_DIPINJAM","pesan":"Buku sedang dipinjam"}}` |
| `POST /buku/1/pinjam?hari=5` | `200 OK` | `{"judul":"Dasar Python","lama_hari":5}` |
| `POST /buku/1/pinjam` (ulang) | `409 Conflict` | `{"detail":{"kode":"BUKU_DIPINJAM","pesan":"Buku sedang dipinjam"}}` |
| `POST /buku/99/pinjam` | `404 Not Found` | `{"detail":"Buku dengan id 99 tidak ditemukan"}` |

Baris keempat menunjukkan efeknya: setelah dipinjam, buku 1 tidak tersedia lagi.

### Validasi tetap berjalan lebih dulu

```powershell
curl.exe -i http://127.0.0.1:8000/buku/0
```

```text
HTTP/1.1 422 Unprocessable Content
{"detail":[{"type":"greater_than_equal","loc":["path","buku_id"],"msg":"Input should be greater than or equal to 1","input":"0","ctx":{"ge":1}}]}
```

Diuji dengan `TestClient`: `POST /buku/99/pinjam?hari=20` menghasilkan `404` (buku diperiksa lebih dulu daripada `hari`), sedangkan `POST /buku/1/pinjam?hari=0` menghasilkan `422`.

Perhatikan bentuk `detail`: pada error buatan kita berupa teks atau objek yang kita pilih, sedangkan pada error validasi berupa daftar. Klien yang membaca `detail` perlu siap dengan keduanya. Keseragaman bentuk error adalah topik proyek tahap 2 dan handler kustom.

### Error di dokumentasi otomatis

Hasil uji pada `main.py` di atas: `/openapi.json` hanya mencatat `200` dan `422` untuk `/buku/{buku_id}`. Error `404`, `400`, dan `409` yang kita `raise` **tidak** otomatis tampil di dokumentasi, sehingga pembaca `/docs` tidak tahu endpoint ini bisa menjawab `404`.

Untuk mendokumentasikannya, pakai parameter `responses` pada dekorator (`main_dokumentasi.py`):

```python title="main_dokumentasi.py"
--8<-- "fastapi/04-penanganan-error/http-exception/main_dokumentasi.py"
```

- `responses` adalah `dict` dengan kunci status code.
- `model` adalah model Pydantic yang menggambarkan isi response error, di sini `{"detail": "..."}`.
- `description` adalah keterangan yang tampil di dokumentasi.

Hasil uji dengan `TestClient`:

- Status yang tercatat menjadi `200`, `404`, dan `422`.
- Entri `404` berisi `"description": "Buku tidak ditemukan"` dan mengacu ke skema `Pesan` (`{"detail": string}`).
- Perilaku endpoint tidak berubah: `/buku/1` menghasilkan `200`, sedangkan `/buku/9` tetap `404` dengan `{"detail":"Buku tidak ditemukan"}`.

`responses` hanya **mendokumentasikan**; kode `raise HTTPException(...)` tetap yang menghasilkan response. Menurut dokumentasi FastAPI, parameter ini juga bisa memuat `headers` dan media type lain; itu tidak dibahas di sini. Tampilan Swagger UI **belum diverifikasi** lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| `return HTTPException(...)` | Diuji dengan `TestClient` (`main_return_salah.py`): response tetap `200` dan isinya objek exception terserialisasi: `{"status_code":404,"detail":"Tidak ditemukan","headers":null}`. Klien mengira berhasil. |
| Memilih `200` atau `400` untuk semua kegagalan | Klien tidak bisa membedakan "tidak ada", "bentrok", dan "salah input". Pilih kode sesuai [Status Code](status-code.md). |
| Mengubah data lalu baru memeriksa error | Data sudah berubah walau response error. Periksa dulu, ubah belakangan. |
| Menaruh pesan internal (jalur file, isi query) di `detail` | Klien bisa membacanya. Tulis pesan yang aman dan berguna bagi pemakai API. |
| Mengira `HTTPException` hanya untuk `404` | Bisa dipakai untuk kode `4xx` apa pun. Contoh di halaman ini: `400`, `404`, `409`. |

## Latihan

1. **Hapus buku.** Tambahkan `DELETE /buku/{buku_id}` dengan status sukses `204`. Jawab `404` bila buku tidak ada dan `409` bila buku sedang dipinjam.
2. **Kembalikan buku.** Tambahkan `POST /buku/{buku_id}/kembali`. Jawab `409` bila buku belum dipinjam.
3. **Prediksi.** Apa status untuk `POST /buku/99/pinjam?hari=20` dan `POST /buku/1/pinjam?hari=0`? Jelaskan urutannya.
4. **Analisis.** Mengapa `HTTPException` harus di-`raise`? Apa yang terjadi bila di-`return`?

??? success "Kunci jawaban"
    Jawaban 1 sampai 3 dijalankan dengan `TestClient` dengan menambahkan endpoint ke `main.py`. Jawaban 4 mengacu pada uji `main_return_salah.py`.

    ```python
    @app.delete("/buku/{buku_id}", status_code=204)
    def hapus_buku(buku_id: IdBuku):
        buku = ambil_buku(buku_id)
        if not buku["tersedia"]:
            raise HTTPException(
                status_code=409, detail="Buku sedang dipinjam, tidak bisa dihapus"
            )
        del buku_db[buku_id]


    @app.post("/buku/{buku_id}/kembali")
    def kembalikan(buku_id: IdBuku):
        buku = ambil_buku(buku_id)
        if buku["tersedia"]:
            raise HTTPException(status_code=409, detail="Buku belum dipinjam")
        buku["tersedia"] = True
        return buku
    ```

    1. `DELETE /buku/99` menghasilkan `404`. `DELETE /buku/2` (sedang dipinjam) menghasilkan `409`. Setelah buku 2 dikembalikan, `DELETE /buku/2` menghasilkan `204`, dan `GET /buku/2` kemudian `404`.
    2. `POST /buku/1/kembali` menghasilkan `409` dengan `{"detail":"Buku belum dipinjam"}`. `POST /buku/2/kembali` menghasilkan `200` dan `"tersedia":true`.
    3. `POST /buku/99/pinjam?hari=20` adalah `404`: `ambil_buku` dipanggil sebelum pemeriksaan `hari`. `POST /buku/1/pinjam?hari=0` adalah `422`: validasi `ge=1` gagal sebelum fungsi dijalankan.
    4. Bila di-`return`, FastAPI memperlakukannya sebagai data biasa: status `200` dengan objek exception sebagai isi. Hanya `raise` yang menghentikan fungsi dan menghasilkan response error.

## Ringkasan

- `HTTPException` menghentikan fungsi dan mengirim status code serta `detail` kepada klien.
- Selalu `raise`, jangan `return`.
- `detail` boleh teks atau objek JSON; `headers` menambah header pada response error.
- Fungsi pembantu yang me-`raise` membuat pemeriksaan tidak ditulis berulang.
- Pilih kode yang tepat: `404` tidak ada, `400` input tidak masuk akal, `409` bentrok dengan keadaan data.
- Validasi parameter selalu berjalan sebelum kode fungsi.
- Error yang di-`raise` tidak otomatis tercatat di dokumentasi; `responses` pada dekorator mendokumentasikannya.
- Periksa dulu, ubah data belakangan.

## Langkah berikutnya

Kembali ke daftar materi di [Modul 04: Penanganan Error](index.md). Materi berikutnya adalah error validasi, yaitu cara membaca dan memahami `422` yang dihasilkan otomatis.
