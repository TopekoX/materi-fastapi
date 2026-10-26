# Operasi CRUD

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan CRUD dan memetakannya ke method HTTP dan operasi SQL.
- [ ] Membuat, membaca (satu dan daftar), mengubah, dan menghapus baris dengan SQLModel.
- [ ] Menambahkan filter dan paginasi pada kueri `select`.
- [ ] Mengubah sebagian data dengan `exclude_unset` dan `sqlmodel_update`.
- [ ] Menjawab `404` untuk baris yang tidak ada.

## Prasyarat

- Sudah membaca [Koneksi ke Basis Data](koneksi-basis-data.md) dan [Model dan Skema](model-dan-skema.md).
- Sudah membaca [Proyek Praktik Tahap 2](../04-penanganan-error/proyek-tahap-2.md) sebagai gambaran CRUD dalam memori.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, **SQLModel 0.0.48**, dan **SQLAlchemy 2.1.6** di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

**CRUD** adalah empat operasi dasar pada data. Pemetaannya:

| Operasi | Method HTTP | SQL | Di halaman ini |
|---|---|---|---|
| **C**reate (buat) | `POST` | `INSERT` | `session.add` + `commit` |
| **R**ead (baca) | `GET` | `SELECT` | `select(...)`, `session.get(...)` |
| **U**pdate (ubah) | `PATCH` / `PUT` | `UPDATE` | ubah atribut objek + `commit` |
| **D**elete (hapus) | `DELETE` | `DELETE` | `session.delete` + `commit` |

Dengan SQLModel kamu tidak menulis SQL langsung. Kamu bekerja dengan objek Python, dan SQLModel menerjemahkannya menjadi SQL. Perubahan baru benar-benar tersimpan setelah `session.commit()`.

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/06-basis-data/operasi-crud/main.py"
```

## Penjelasan kode

### Model dan skema

`TugasDasar`, `Tugas`, `TugasBuat`, dan `TugasPublik` sama seperti di [Model dan Skema](model-dan-skema.md). Kelas baru `TugasUbah` dipakai untuk `PATCH`: semua field-nya opsional, karena klien hanya mengirim yang ingin diubah.

### Fungsi pembantu

```python
def cari_tugas(session: Session, tugas_id: int) -> Tugas:
    tugas = session.get(Tugas, tugas_id)
    if tugas is None:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")
    return tugas
```

`session.get(Tugas, tugas_id)` mengambil satu baris berdasarkan kunci utama, atau `None` bila tidak ada. Pemeriksaan `404` ditulis sekali dan dipakai tiga endpoint (baca satu, ubah, hapus), seperti pola di [HTTPException](../04-penanganan-error/http-exception.md).

### Create

```python
@app.post("/tugas", response_model=TugasPublik, status_code=201)
def buat_tugas(data: TugasBuat, session: SessionDep):
    tugas = Tugas.model_validate(data)
    session.add(tugas)
    session.commit()
    session.refresh(tugas)
    return tugas
```

`model_validate` mengubah `TugasBuat` menjadi objek tabel `Tugas`. `add` mendaftarkan, `commit` menyimpan, `refresh` memuat ulang agar `id` terisi.

### Read: daftar dengan filter dan paginasi

```python
pernyataan = select(Tugas)
if selesai is not None:
    pernyataan = pernyataan.where(Tugas.selesai == selesai)
if cari is not None:
    pernyataan = pernyataan.where(col(Tugas.judul).contains(cari))
return session.exec(pernyataan.offset(offset).limit(limit)).all()
```

- `select(Tugas)` setara `SELECT * FROM tugas`.
- `.where(...)` menambah kondisi dan boleh dirangkai. Filter hanya ditambahkan bila parameternya dikirim.
- `col(Tugas.judul).contains(cari)` mencari teks yang mengandung `cari`. `col(...)` memberi tahu editor bahwa ini kolom.
- `.offset(offset).limit(limit)` memotong hasil: lewati `offset` baris, ambil paling banyak `limit`. Ini paginasi pada tingkat basis data, berbeda dengan memotong list di Python seperti di [Proyek Tahap 1](../03-data-validasi/proyek-tahap-1.md).
- `session.exec(...).all()` menjalankan kueri dan mengembalikan semua hasil sebagai list. `limit` dibatasi `le=100` dengan `Query` agar klien tidak meminta terlalu banyak.

### Update: mengubah sebagian

```python
tugas = cari_tugas(session, tugas_id)
perubahan = data.model_dump(exclude_unset=True)
tugas.sqlmodel_update(perubahan)
session.add(tugas)
session.commit()
session.refresh(tugas)
```

- `model_dump(exclude_unset=True)` hanya berisi field yang benar-benar dikirim klien (prinsip yang sama dengan di [Proyek Tahap 2](../04-penanganan-error/proyek-tahap-2.md)).
- `sqlmodel_update(perubahan)` menimpa atribut objek dengan nilai tersebut. Field yang tidak dikirim tidak disentuh.
- Setelah `commit`, `refresh` memuat nilai terbaru dari basis data.

### Delete

```python
tugas = cari_tugas(session, tugas_id)
session.delete(tugas)
session.commit()
```

Objek ditandai untuk dihapus dengan `session.delete`, dan baris benar-benar hilang saat `commit`. Endpoint menjawab `204` tanpa isi.

## Menjalankan

```powershell
pip install sqlmodel
fastapi dev main.py
```

Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah. Berkas `database.db` dibuat di folder kerja.

## Mencoba request

Hasil di bawah dijalankan berurutan dengan `curl.exe` dari keadaan tanpa `database.db` (`-i` menampilkan baris status; body dikirim dari file JSON dengan header `Content-Type: application/json`).

### Create

| Body | Status | Isi |
|---|---|---|
| `{"judul":"Belajar SQLModel","catatan":"Modul 06","prioritas":1}` | `201` | `{"judul":"Belajar SQLModel","catatan":"Modul 06","prioritas":1,"selesai":false,"id":1}` |
| `{"judul":"Cuci motor"}` | `201` | `{"judul":"Cuci motor","catatan":null,"prioritas":2,"selesai":false,"id":2}` |
| `{"judul":"Baca dokumentasi","prioritas":3}` | `201` | tugas dengan `"id":3` |

### Read

| Request | Status | Isi |
|---|---|---|
| `GET /tugas` | `200` | ketiga tugas |
| `GET /tugas?cari=motor` | `200` | hanya tugas 2 |
| `GET /tugas?limit=1&offset=1` | `200` | hanya tugas 2 (lewati satu, ambil satu) |
| `GET /tugas/2` | `200` | tugas 2 |
| `GET /tugas?limit=0` | `422` | `greater_than_equal`, `loc` `["query","limit"]` |

### Update

| Request | Status | Isi |
|---|---|---|
| `PATCH /tugas/1`, `{"selesai":true,"catatan":null}` | `200` | `{"judul":"Belajar SQLModel","catatan":null,"prioritas":1,"selesai":true,"id":1}` |
| `GET /tugas?selesai=true` | `200` | hanya tugas 1 |
| `GET /tugas?selesai=false` | `200` | tugas 2 dan 3 |
| `PATCH /tugas/1`, `{"prioritas":7}` | `422` | `less_than_equal` |
| `PATCH /tugas/2`, `{}` | `200` | tugas 2 tidak berubah |
| `PATCH /tugas/99` | `404` | `{"detail":"Tugas tidak ditemukan"}` |

Perhatikan `PATCH` pertama: hanya `selesai` dan `catatan` yang berubah; `judul` dan `prioritas` tetap.

### Delete

| Request | Status | Isi |
|---|---|---|
| `DELETE /tugas/2` | `204` | tanpa isi |
| `GET /tugas/2` | `404` | `{"detail":"Tugas tidak ditemukan"}` |
| `DELETE /tugas/2` (ulang) | `404` | sama |
| `GET /tugas` | `200` | hanya tugas 1 dan 3 |

### Temuan: `null` pada field wajib

Dengan `TestClient`, `PATCH /tugas/2` dengan body `{"judul": null}` menghasilkan `500`, bukan `422`. Skema `TugasUbah` mengizinkan `judul` bernilai `null` (agar field boleh tidak dikirim), tetapi kolom `judul` di tabel wajib terisi, sehingga basis data yang menolak. Data tugas 2 tetap utuh sesudahnya. Cara menanganinya, misalnya menolak `null` untuk field wajib seperti pada [Proyek Tahap 2](../04-penanganan-error/proyek-tahap-2.md), tidak diterapkan di contoh ini, tetapi harus kamu waspadai di kode nyata.

### Dokumentasi otomatis

Semua endpoint tampil di `/docs`. Tampilan visual Swagger UI **belum diverifikasi** lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Lupa `session.commit()` | Perubahan tidak tersimpan. Tidak dijalankan di sini. |
| Mengubah objek tetapi lupa `session.add` | Pada contoh ini objek sudah berasal dari session, tetapi menuliskan `add` menjaga kebiasaan yang konsisten. |
| Memakai `model_dump()` tanpa `exclude_unset=True` pada `PATCH` | Field yang tidak dikirim ikut menimpa data dengan nilai default. Tidak dijalankan di sini. |
| Mengirim `null` untuk field wajib di `PATCH` | `500` dari basis data (teruji). Tolak sebelum disimpan. |
| Tidak membatasi `limit` | Klien bisa meminta data sangat besar. Batasi dengan `Query(le=...)`. |
| Mengira `.all()` mengambil satu baris | `.all()` mengembalikan list. Untuk satu baris pakai `session.get(...)` atau `.first()`. `.first()` tidak dijalankan di sini. |
| Menghapus tanpa memeriksa keberadaan | Pada contoh ini, `404` (teruji). Pola ini mencegah `500`. |

## Latihan

1. **Hitung.** Buat `GET /ringkasan` yang mengembalikan `total` tugas dan jumlah yang `selesai`.
2. **Urut.** Urutkan tugas dari prioritas tertinggi nilainya, lalu berdasarkan judul.
3. **Prediksi.** Apa status `PATCH /tugas/2` dengan body `{"judul": null}`? Mengapa bukan `422`?
4. **Analisis.** Mengapa `DELETE` menjawab `204`, bukan `200` dengan isi?

??? success "Kunci jawaban"
    Jawaban 1 dan 2 dijalankan dengan `TestClient`. Jawaban 3 dari hasil uji di atas. Jawaban 4 adalah penalaran.

    ```python
    from sqlmodel import col, func, select

    @app.get("/ringkasan")
    def ringkasan(session: SessionDep):
        total = session.exec(select(func.count()).select_from(Tugas)).one()
        selesai = session.exec(
            select(func.count()).select_from(Tugas).where(Tugas.selesai == True)
        ).one()
        return {"total": total, "selesai": selesai}


    @app.get("/urut")
    def urut(session: SessionDep):
        pernyataan = select(Tugas).order_by(col(Tugas.prioritas).desc(), Tugas.judul)
        return [t.judul for t in session.exec(pernyataan).all()]
    ```

    1. Dengan tiga tugas dan satu selesai: `{"total":3,"selesai":1}`.
    2. Dengan prioritas 1, 3, dan 3 dan judul `B satu`, `A dua`, `C tiga`: `["A dua","C tiga","B satu"]`.
    3. `500`. `TugasUbah` mengizinkan `null`, tetapi kolom di tabel wajib terisi sehingga basis data menolak dan FastAPI tidak sempat memberi `422`.
    4. `204` berarti berhasil dan tidak ada isi untuk dikembalikan, sesuai pembahasan di [Status Code](../04-penanganan-error/status-code.md).

## Ringkasan

- CRUD: `POST`/`INSERT`, `GET`/`SELECT`, `PATCH`/`UPDATE`, `DELETE`.
- Menyimpan: `add` → `commit` → `refresh`. Menghapus: `delete` → `commit`.
- `select(...).where(...).offset(...).limit(...)` membangun kueri dengan filter dan paginasi.
- `session.get(Model, id)` mengambil satu baris, atau `None`.
- `PATCH` memakai `model_dump(exclude_unset=True)` dan `sqlmodel_update`.
- Periksa keberadaan baris dulu dan jawab `404` bila tidak ada.
- Waspadai `null` untuk field wajib pada skema ubah.

## Langkah berikutnya

Lanjut ke [Relasi](relasi.md), atau kembali ke daftar materi di [Modul 06: Basis Data](index.md).
