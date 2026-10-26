# Proyek Praktik Tahap 2

## Tujuan pembelajaran

Setelah mengerjakan halaman ini, kamu mampu:

- [ ] Mengembangkan proyek tahap 1 tanpa memulai dari nol.
- [ ] Menerapkan satu format error untuk seluruh API dengan exception handler.
- [ ] Menambahkan aturan bisnis yang menghasilkan `409` (judul tidak boleh kembar).
- [ ] Membuat endpoint `PATCH` untuk mengubah sebagian data.
- [ ] Memakai konstanta `status` agar kode status mudah dibaca.

## Prasyarat

- Sudah mengerjakan [Proyek Praktik Tahap 1](../03-data-validasi/proyek-tahap-1.md).
- Sudah membaca [Status Code](status-code.md), [HTTPException](http-exception.md), [Error Validasi](error-validasi.md), dan [Handler Error Kustom](handler-kustom.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, dan **Pydantic 2.14.1** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Tentang tahap ini

Tahap 2 melanjutkan **TugasKu API** dari tahap 1. Daftar endpoint dan model dasar tidak berubah. Yang bertambah:

| Perubahan | Dibahas di |
|---|---|
| Satu format error: `{"galat": {"kode", "pesan", "rincian"}}` | [Handler Error Kustom](handler-kustom.md) |
| Exception sendiri `TugasTidakDitemukan` dan `JudulSudahAda` | [Handler Error Kustom](handler-kustom.md) |
| Aturan: judul tidak boleh kembar (huruf besar-kecil diabaikan), `409` | [HTTPException](http-exception.md) |
| `PATCH /tugas/{id}` untuk ubah sebagian | halaman ini |
| Konstanta `status.HTTP_...` | [Status Code](status-code.md) |

Penyimpanan masih di memori; basis data baru di tahap 3.

### Kebutuhan

| Operasi | Method dan path | Sukses | Kemungkinan error |
|---|---|---|---|
| Buat | `POST /tugas` | `201` | `422`, `409` judul kembar |
| Daftar | `GET /tugas` | `200` | `422` |
| Ambil satu | `GET /tugas/{id}` | `200` | `404`, `422` |
| Ganti seluruhnya | `PUT /tugas/{id}` | `200` | `404`, `409`, `422` |
| Ubah sebagian | `PATCH /tugas/{id}` | `200` | `400`, `404`, `409`, `422` |
| Hapus | `DELETE /tugas/{id}` | `204` | `404`, `422` |

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/proyek/tahap-2/main.py"
```

## Penjelasan kode

### Tiga model

`TugasInput` dan `Tugas` sama seperti tahap 1. Model baru `TugasUbah` dipakai oleh `PATCH`: semua field-nya opsional (`= None`), karena klien hanya mengirim yang ingin diubah. Aturan `Field` (panjang, rentang) tetap berlaku untuk field yang dikirim.

### Exception dan handler

```python
class TugasTidakDitemukan(Exception): ...
class JudulSudahAda(Exception): ...
```

Dua exception ini membawa data (`tugas_id`, `judul`) dan masing-masing punya handler yang menjawab `404` dan `409`. Fungsi `respons_galat` membentuk semua response error supaya seragam. Handler untuk `StarletteHTTPException`, `RequestValidationError`, dan `Exception` bekerja sama seperti di [Handler Error Kustom](handler-kustom.md).

Konstanta seperti `status.HTTP_404_NOT_FOUND` menggantikan angka mentah di handler.

### Fungsi pembantu

```python
def cari_tugas(tugas_id: int) -> Tugas:
    if tugas_id not in tugas_db:
        raise TugasTidakDitemukan(tugas_id)
    return tugas_db[tugas_id]


def pastikan_judul_unik(judul: str, abaikan_id: int | None = None) -> None:
    for tugas in tugas_db.values():
        if tugas.id != abaikan_id and tugas.judul.lower() == judul.lower():
            raise JudulSudahAda(judul)
```

- `cari_tugas` sekarang me-raise exception sendiri, bukan `HTTPException`.
- `pastikan_judul_unik` membandingkan judul tanpa memperhatikan huruf besar-kecil (`lower()`).
- `abaikan_id` dipakai saat mengubah: sebuah tugas boleh tetap memakai judulnya sendiri, tetapi tidak boleh sama dengan judul tugas lain.

### `PATCH`: ubah sebagian

```python
@app.patch("/tugas/{tugas_id}", response_model=Tugas)
def ubah_tugas(tugas_id: IdTugas, data: TugasUbah):
    tugas = cari_tugas(tugas_id)
    perubahan = data.model_dump(exclude_unset=True)
    for nama in ("judul", "prioritas", "selesai"):
        if nama in perubahan and perubahan[nama] is None:
            raise HTTPException(status_code=400, detail=f"Field '{nama}' tidak boleh null")
    if "judul" in perubahan:
        pastikan_judul_unik(perubahan["judul"], abaikan_id=tugas_id)
    tugas_baru = tugas.model_copy(update=perubahan)
    tugas_db[tugas_id] = tugas_baru
    return tugas_baru
```

- `model_dump(exclude_unset=True)` hanya berisi field yang **benar-benar dikirim** klien. Ini prinsip yang sama dengan `response_model_exclude_unset` di [Response Model](../03-data-validasi/response-model.md).
- Klien boleh mengirim `null` hanya untuk `catatan` (artinya menghapus catatan). Untuk `judul`, `prioritas`, dan `selesai`, `null` tidak masuk akal sehingga dijawab `400`.
- `model_copy(update=perubahan)` membuat salinan `tugas` dengan nilai baru. Metode ini tidak memvalidasi ulang nilai; validasi sudah dilakukan lewat `TugasUbah` dan pemeriksaan kita.
- Pemeriksaan (`404`, `400`, `409`) semuanya di depan; data baru disimpan setelah lolos.

## Menjalankan

```powershell
fastapi dev main.py
```

Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah.

## Mencoba request

Hasil di bawah dari server `fastapi dev` yang dijalankan berurutan dari keadaan kosong, dengan `curl.exe` dan body JSON dari file (`-d "@berkas.json"`, header `Content-Type: application/json`).

### Buat dan judul kembar

| Body | Hasil |
|---|---|
| `{"judul":"Belajar FastAPI","catatan":"Modul 04","prioritas":1}` | `201` `{"judul":"Belajar FastAPI","catatan":"Modul 04","prioritas":1,"selesai":false,"id":1}` |
| `{"judul":"belajar fastapi"}` | `409` `{"galat":{"kode":"JUDUL_SUDAH_ADA","pesan":"Judul 'belajar fastapi' sudah dipakai","rincian":[]}}` |
| `{"judul":"Cuci motor"}` | `201` dengan `"id":2` |
| `{"judul":"ab","prioritas":9}` | `422` (lihat di bawah) |

Body terakhir:

```json
{"galat":{"kode":"VALIDASI_GAGAL","pesan":"Data yang dikirim tidak valid","rincian":[{"field":"body.judul","jenis":"string_too_short","pesan":"String should have at least 3 characters"},{"field":"body.prioritas","jenis":"less_than_equal","pesan":"Input should be less than or equal to 3"}]}}
```

### `PATCH`

| Request | Hasil |
|---|---|
| `PATCH /tugas/1` body `{"selesai":true,"catatan":null}` | `200` `{"judul":"Belajar FastAPI","catatan":null,"prioritas":1,"selesai":true,"id":1}`. Hanya `selesai` dan `catatan` yang berubah. |
| `PATCH /tugas/1` body `{"judul":null}` | `400` `{"galat":{"kode":"HTTP_400","pesan":"Field 'judul' tidak boleh null","rincian":[]}}` |
| `PATCH /tugas/1` body `{"judul":"Cuci motor"}` | `409` `{"galat":{"kode":"JUDUL_SUDAH_ADA","pesan":"Judul 'Cuci motor' sudah dipakai","rincian":[]}}` |
| `PATCH /tugas/1` body `{"prioritas":7}` | `422` dengan `"field":"body.prioritas"`, `"jenis":"less_than_equal"` |
| `PATCH /tugas/99` | `404` `{"galat":{"kode":"TUGAS_TIDAK_ADA","pesan":"Tugas dengan id 99 tidak ditemukan","rincian":[]}}` |

### `PUT`, daftar, dan hapus

| Request | Hasil |
|---|---|
| `PUT /tugas/2` dengan judul `Belajar FastAPI` | `409` `JUDUL_SUDAH_ADA` |
| `PUT /tugas/2` dengan judul `Cuci motor` (judul sendiri) | `200` |
| `GET /tugas?selesai=true` | `200` berisi tugas 1 |
| `GET /tugas?halaman=0` | `422`, `"field":"query.halaman"` |
| `GET /tugas/99` | `404` `TUGAS_TIDAK_ADA` |
| `GET /tugas/0` | `422`, `"field":"path.tugas_id"` |
| `DELETE /tugas/2` | `204` tanpa isi |
| `DELETE /tugas/2` (ulang) | `404` `TUGAS_TIDAK_ADA` |
| `GET /nope` | `404` `{"galat":{"kode":"HTTP_404","pesan":"Not Found","rincian":[]}}` |

Perbedaan dengan tahap 1: semua error kini berbentuk `{"galat": ...}`, dan `PATCH` bisa mengubah sebagian data tanpa mengosongkan field lain (bandingkan dengan `PUT` di tahap 1 yang mengembalikan `catatan` ke `null`).

!!! warning "Keterbatasan tahap 2"
    - Data masih hilang saat server dimulai ulang (dalam memori). Tidak diuji dengan memulai ulang server.
    - Tidak ada pengguna atau login; siapa pun bisa mengubah dan menghapus.
    - `500` belum diuji untuk proyek ini (handler `Exception` identik dengan [Handler Error Kustom](handler-kustom.md), yang sudah diuji).
    - Tampilan Swagger UI belum diverifikasi lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Memakai `model_dump()` tanpa `exclude_unset=True` pada `PATCH` | Field yang tidak dikirim ikut menimpa data dengan `None`. Tidak dijalankan di sini; prinsipnya sama dengan `exclude_unset` di Response Model. |
| Lupa `abaikan_id` saat mengubah judul | Tugas dianggap bentrok dengan dirinya sendiri sehingga mengirim judul yang sama dijawab `409`. |
| Membandingkan judul tanpa `lower()` | `"Cuci Motor"` dan `"cuci motor"` dianggap berbeda. |
| Mengubah data sebelum semua pemeriksaan selesai | Response error, tetapi data sudah berubah. Periksa dulu, ubah belakangan. |
| Menulis bentuk error di setiap endpoint | Format akan tidak seragam. Serahkan ke handler. |

## Latihan

1. **Aturan baru.** Tugas yang belum selesai tidak boleh dihapus. Jawab `409` dengan kode `TUGAS_BELUM_SELESAI`.
2. **Prediksi.** Apa hasil `PATCH /tugas/1` dengan body `{}`?
3. **Prediksi 2.** Bagaimana cara menghapus `catatan` sebuah tugas lewat `PATCH`?
4. **Analisis.** Mengapa `PUT /tugas/2` dengan judul tugas 2 sendiri tidak dijawab `409`?

??? success "Kunci jawaban"
    Jawaban 1 dan 2 dijalankan dengan `TestClient` (route `DELETE` lama diganti untuk uji). Jawaban 3 dari hasil `curl` di atas, jawaban 4 dari kode.

    ```python
    class TugasBelumSelesai(Exception):
        def __init__(self, tugas_id: int):
            self.tugas_id = tugas_id


    @app.exception_handler(TugasBelumSelesai)
    async def tugas_belum_selesai_handler(request: Request, exc: TugasBelumSelesai):
        return respons_galat(409, "TUGAS_BELUM_SELESAI", f"Tugas {exc.tugas_id} belum selesai, tidak bisa dihapus")


    @app.delete("/tugas/{tugas_id}", status_code=204)
    def hapus_tugas(tugas_id: IdTugas):
        tugas = cari_tugas(tugas_id)
        if not tugas.selesai:
            raise TugasBelumSelesai(tugas_id)
        del tugas_db[tugas_id]
    ```

    1. Hapus tugas yang belum selesai: `409` dengan `{"galat":{"kode":"TUGAS_BELUM_SELESAI","pesan":"Tugas 1 belum selesai, tidak bisa dihapus","rincian":[]}}`. Setelah ditandai selesai lewat `PATCH`, `DELETE` menghasilkan `204`, dan `GET` berikutnya `404`.
    2. `200`, tugas tidak berubah: `{"judul":"Satu","catatan":null,"prioritas":2,"selesai":false,"id":1}`.
    3. Kirim `{"catatan": null}`. `catatan` adalah satu-satunya field yang boleh `null`; hasil `curl` di atas menunjukkan `"catatan":null`.
    4. Karena `pastikan_judul_unik` menerima `abaikan_id` dan melewati tugas dengan id itu.

## Ringkasan

- Tahap 2 menambah format error seragam, aturan judul unik, dan `PATCH` di atas tahap 1.
- Exception sendiri plus handler memisahkan "apa yang terjadi" dari "bagaimana dijawab".
- `409` dipakai untuk bentrokan dengan data yang ada, `404` untuk data tidak ada, `400` untuk input yang tidak masuk akal, `422` untuk validasi.
- `PATCH` memakai model dengan field opsional dan `model_dump(exclude_unset=True)`.
- Periksa dulu, ubah data belakangan.

## Langkah berikutnya

Kembali ke [Modul 04: Penanganan Error](index.md). Modul berikutnya adalah Modul 05: Dependency Injection.
