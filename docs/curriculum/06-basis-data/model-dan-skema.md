# Model dan Skema

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Membedakan **model tabel** (yang disimpan) dari **skema API** (yang dikirim dan diterima).
- [ ] Menyusun kelas dasar yang dipakai bersama lewat pewarisan.
- [ ] Membuat skema input yang tidak memuat `id` atau kolom internal.
- [ ] Membuat skema output dengan `response_model` agar kolom internal tidak bocor.
- [ ] Menjelaskan mengapa menambah field ke model tidak mengubah tabel yang sudah ada.

## Prasyarat

- Sudah membaca [Koneksi ke Basis Data](koneksi-basis-data.md).
- Sudah membaca [Response Model](../03-data-validasi/response-model.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **SQLModel 0.0.48**, dan **SQLAlchemy 2.1.6** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Di halaman sebelumnya satu kelas `Catatan` melayani tiga peran sekaligus: tabel, body request, dan response. Hasilnya dua masalah yang teramati:

- body kosong tidak menghasilkan `422`, melainkan `500` dari basis data,
- semua kolom, termasuk yang internal, ikut keluar dalam response.

Solusinya: pisahkan **model** dan **skema**.

| Peran | Pertanyaan yang dijawab | Contoh di halaman ini |
|---|---|---|
| **Model tabel** | Apa yang disimpan di basis data? | `Tugas` (`table=True`) |
| **Skema input** | Apa yang boleh dikirim klien? | `TugasBuat` |
| **Skema output** | Apa yang dikembalikan ke klien? | `TugasPublik` |

Prinsipnya sama dengan [Response Model](../03-data-validasi/response-model.md): input dan output tidak harus sama dengan data yang disimpan. Perbedaannya, kini ada satu lapisan lagi di tengah, yaitu tabel.

Menurut dokumentasi FastAPI, pemisahan ini juga menjaga agar `id` dibuat oleh server dan klien tidak menentukannya, sebab klien bisa saja menimpa data yang sudah ada.

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/06-basis-data/model-dan-skema/main.py"
```

## Penjelasan kode

### Kelas dasar dengan aturan

```python
class TugasDasar(SQLModel):
    judul: str = Field(min_length=3, max_length=100)
    catatan: str | None = Field(default=None, max_length=500)
    prioritas: int = Field(default=2, ge=1, le=3)
    selesai: bool = False
```

Tanpa `table=True`, `SQLModel` bertindak sebagai model Pydantic biasa, termasuk aturan `Field` yang kamu kenal dari [Validasi Field](../03-data-validasi/validasi-field.md). Field yang dimiliki bersama ditulis di sini **sekali**.

### Model tabel

```python
class Tugas(TugasDasar, table=True):
    id: int | None = Field(default=None, primary_key=True)
    catatan_internal: str | None = None
```

`Tugas` mewarisi semua field dasar, lalu menambah `id` (dibuat basis data) dan `catatan_internal` (kolom yang tidak boleh dilihat klien). Hanya kelas dengan `table=True` yang menjadi tabel.

### Skema input dan output

```python
class TugasBuat(TugasDasar):
    pass


class TugasPublik(TugasDasar):
    id: int
```

- `TugasBuat` tidak punya `id` maupun `catatan_internal`, sehingga klien tidak bisa mengisinya.
- `TugasPublik` menambah `id` (wajib ada pada output) tetapi tidak memuat `catatan_internal`.

### Alur membuat tugas

```python
@app.post("/tugas", response_model=TugasPublik, status_code=201)
def buat_tugas(data: TugasBuat, session: SessionDep):
    tugas = Tugas.model_validate(data, update={"catatan_internal": "dibuat lewat API"})
    session.add(tugas)
    session.commit()
    session.refresh(tugas)
    return tugas
```

1. FastAPI memvalidasi body terhadap `TugasBuat` (aturan `Field` berlaku, kegagalan menjadi `422`).
2. `Tugas.model_validate(data, update={...})` membuat objek `Tugas` dari `data` dan menambahkan nilai yang diisi server.
3. `add`, `commit`, `refresh` menyimpan objek dan memuat `id` yang dibuat basis data.
4. `response_model=TugasPublik` menyaring hasil sebelum dikirim.

Endpoint `/tugas/{id}/mentah` sengaja ada **hanya untuk percobaan**: ia mengembalikan model tabel tanpa `response_model`, untuk membuktikan apa yang bocor tanpa filter.

## Menjalankan

```powershell
pip install sqlmodel
fastapi dev main.py
```

Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah. Berkas `database.db` dibuat di folder kerja.

## Mencoba request

Hasil di bawah dijalankan dengan `curl.exe` dari keadaan tanpa `database.db`.

### Membuat tugas

Body `{"judul":"Belajar SQLModel","catatan":"Modul 06","prioritas":1}`:

```text
HTTP/1.1 201 Created
{"judul":"Belajar SQLModel","catatan":"Modul 06","prioritas":1,"selesai":false,"id":1}
```

### Validasi kembali berfungsi

Body `{"judul":"ab","prioritas":9}`:

```text
HTTP/1.1 422 Unprocessable Content
{"detail":[{"type":"string_too_short","loc":["body","judul"],"msg":"String should have at least 3 characters","input":"ab","ctx":{"min_length":3}},{"type":"less_than_equal","loc":["body","prioritas"],"msg":"Input should be less than or equal to 3","input":9,"ctx":{"le":3}}]}
```

Bandingkan dengan halaman sebelumnya yang menghasilkan `500` untuk body kosong: kini kesalahan klien dijawab `422`, sebelum menyentuh basis data.

### Klien tidak bisa menentukan `id` atau kolom internal

Body `{"id":99,"judul":"Coba kirim id","catatan_internal":"retas"}`:

```text
HTTP/1.1 201 Created
{"judul":"Coba kirim id","catatan":null,"prioritas":2,"selesai":false,"id":2}
```

Nilai `id` 99 diabaikan; basis data memberi `id` 2. Field `catatan_internal` yang dikirim klien juga diabaikan, terbukti pada pemeriksaan berikut.

### Yang tersimpan versus yang dikirim

`GET /tugas/1` (lewat `TugasPublik`):

```json
{"judul":"Belajar SQLModel","catatan":"Modul 06","prioritas":1,"selesai":false,"id":1}
```

`GET /tugas/1/mentah` (model tabel apa adanya):

```json
{"id":1,"catatan":"Modul 06","prioritas":1,"selesai":false,"judul":"Belajar SQLModel","catatan_internal":"dibuat lewat API"}
```

Kolom `catatan_internal` ada di tabel, tetapi tersaring dari response yang memakai `response_model`. Pada tugas kedua, `catatan_internal` juga bernilai `"dibuat lewat API"` (nilai yang diisi server), bukan `"retas"` dari klien.

### Skema di dokumentasi otomatis

`/openapi.json` memuat skema `TugasBuat` (field `judul`, `catatan`, `prioritas`, `selesai`; wajib: `judul`) dan `TugasPublik` (menambah `id`; wajib: `judul`, `id`). Model tabel `Tugas` **tidak** muncul sebagai skema, sebab tidak dipakai sebagai body maupun response. Tampilan visual Swagger UI **belum diverifikasi** lewat browser.

### Menambah field tidak mengubah tabel lama

Diuji dengan skrip terpisah: tabel `tugas` dibuat dengan kolom `id` dan `judul`, satu baris disimpan, lalu model diubah dengan menambah `label` dan `create_all` dijalankan lagi. Hasil saat membaca:

```text
OperationalError (sqlite3.OperationalError) no such column: tugas.label
```

`create_all` tidak menambah kolom ke tabel yang sudah ada. Pada tahap belajar, kamu bisa menghapus `database.db` agar dibuat ulang, tetapi data hilang. Cara yang benar adalah migrasi, di halaman [Migrasi](migrasi.md).

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Memakai model tabel sebagai body request | Tidak ada validasi `422` yang andal, dan klien bisa mencoba mengisi kolom yang seharusnya milik server. Pakai skema input. |
| Mengembalikan model tabel tanpa `response_model` | Kolom internal ikut keluar (teruji di `/mentah`). |
| Menyalin semua field ke setiap kelas | Duplikasi. Pakai kelas dasar dan pewarisan. |
| Menaruh `id` di skema input | Klien bisa menentukan `id`. Dokumentasi FastAPI mengingatkan hal ini. |
| Menambah field ke model lalu mengira tabel ikut berubah | `no such column` (teruji). Pakai migrasi atau buat ulang tabel. |
| Menyimpan kata sandi mentah di kolom | Tidak aman. Kata sandi di-hash dahulu; dibahas di Modul 07. |

## Latihan

1. **Dasar.** Sebutkan tiga peran kelas di halaman ini dan kelas yang menjalankannya.
2. **Prediksi.** Apa `id` tugas bila klien mengirim `{"id": 99, "judul": "Contoh"}`? Mengapa?
3. **Analisis.** Mengapa `catatan_internal` tidak ada di `TugasBuat` maupun `TugasPublik`?
4. **Praktik.** Tambahkan field `label: str | None = None` ke `TugasDasar`. Apa yang terjadi bila `database.db` lama dipertahankan?

??? success "Kunci jawaban"
    Jawaban 2 dan 4 mengacu pada hasil uji di atas.

    1. Model tabel: `Tugas`. Skema input: `TugasBuat`. Skema output: `TugasPublik`.
    2. `id` ditentukan basis data, bukan klien. Pada percobaan, `id` 99 diabaikan dan tugas mendapat `id` berikutnya.
    3. `catatan_internal` milik server (diisi di `buat_tugas`) dan tidak untuk dilihat klien. Dengan tidak menaruhnya di skema input, klien tidak bisa mengisinya; dengan tidak menaruhnya di skema output, ia tidak bocor.
    4. `label` otomatis ada di `TugasBuat` dan `TugasPublik` karena pewarisan. Namun tabel lama tidak memiliki kolom `label`, sehingga membaca tugas menghasilkan `OperationalError: no such column` (teruji pada skrip terpisah). Hapus `database.db` untuk dibuat ulang, atau pakai migrasi.

## Ringkasan

- **Model tabel** menggambarkan apa yang disimpan; **skema** menggambarkan apa yang masuk dan keluar API.
- Gunakan kelas dasar untuk field bersama, lalu turunkan: tabel (`table=True`), input, dan output.
- Skema input tanpa `id` dan kolom internal; skema output lewat `response_model`.
- Aturan validasi tetap berlaku pada skema non-tabel, sehingga `422` kembali berfungsi.
- `create_all` hanya membuat tabel baru; perubahan struktur butuh migrasi.

## Langkah berikutnya

Lanjut ke [Operasi CRUD](operasi-crud.md), atau kembali ke daftar materi di [Modul 06: Basis Data](index.md).
