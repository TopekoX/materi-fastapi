# Proyek Praktik Tahap 1

## Tujuan pembelajaran

Setelah mengerjakan halaman ini, kamu mampu:

- [ ] Merancang API CRUD sederhana dari daftar kebutuhan.
- [ ] Menggabungkan request body, model Pydantic, validasi field, validasi parameter, dan response model dalam satu aplikasi.
- [ ] Menyimpan data di memori dan membuat ID otomatis.
- [ ] Membuat endpoint buat, daftar (dengan filter dan paginasi), ambil satu, ganti, dan hapus.
- [ ] Menjawab `404` untuk data yang tidak ada.

## Prasyarat

- Semua materi sebelumnya di Modul 03: [Request Body](request-body.md), [Model Pydantic](model-pydantic.md), [Validasi Field](validasi-field.md), [Validasi Path dan Query Parameter](validasi-path-query.md), dan [Response Model](response-model.md).
- [Urutan Route](../02-dasar-routing/urutan-route.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7**, **FastAPI 0.162.0**, dan **Pydantic 2.14.1** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Tentang proyek ini

Ini tahap pertama dari satu proyek yang tumbuh sepanjang kurikulum: **TugasKu API**, API manajemen tugas (to-do). Tahap-tahap berikutnya menambah fitur di atas hasil tahap ini. Rencana lengkapnya ada di [Peta Belajar](../../peta-belajar.md#proyek-praktik).

Tahap 1 menghasilkan **CRUD dalam memori**. CRUD adalah empat operasi dasar pada data: *Create* (buat), *Read* (baca), *Update* (ubah), *Delete* (hapus). "Dalam memori" berarti data disimpan di variabel Python, jadi **hilang saat server dimulai ulang**. Basis data baru dibahas di Modul 06.

### Kebutuhan

| Operasi | Method dan path | Hasil sukses |
|---|---|---|
| Buat tugas | `POST /tugas` | `201` dan tugas baru |
| Daftar tugas | `GET /tugas` | `200` dan daftar, dengan filter `selesai`, `cari`, dan paginasi |
| Ambil satu | `GET /tugas/{tugas_id}` | `200` dan satu tugas |
| Ganti tugas | `PUT /tugas/{tugas_id}` | `200` dan tugas yang sudah diganti |
| Hapus tugas | `DELETE /tugas/{tugas_id}` | `204` tanpa isi |

Aturan data: `judul` 3 sampai 100 karakter, `catatan` opsional maksimal 500 karakter, `prioritas` 1 sampai 3, dan `selesai` berdefault `false`. Tugas yang tidak ditemukan dijawab `404`.

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/proyek/tahap-1/main.py"
```

## Penjelasan kode

### Dua model

```python
class TugasInput(BaseModel):
    judul: str = Field(min_length=3, max_length=100)
    catatan: str | None = Field(default=None, max_length=500)
    prioritas: int = Field(default=2, ge=1, le=3, description="1 = tinggi, 3 = rendah")
    selesai: bool = False


class Tugas(TugasInput):
    id: int
```

`TugasInput` adalah data yang **dikirim klien**. `Tugas` mewarisinya dan menambah `id`, yang dibuat server dan tidak boleh ditentukan klien. `Tugas` juga dipakai sebagai response model.

### Penyimpanan dan ID

```python
tugas_db: dict[int, Tugas] = {}
id_berikutnya = 1
```

`tugas_db` adalah `dict` dengan ID sebagai kunci, sehingga mencari tugas lewat ID cepat. `id_berikutnya` menghitung ID yang akan diberikan.

### Parameter path yang dipakai ulang

```python
IdTugas = Annotated[int, Path(ge=1, title="ID tugas")]
```

Tipe `Annotated` disimpan dalam satu nama supaya aturan "ID minimal 1" tidak ditulis berulang di tiga endpoint.

### Fungsi pembantu dan `404`

```python
def cari_tugas(tugas_id: int) -> Tugas:
    if tugas_id not in tugas_db:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")
    return tugas_db[tugas_id]
```

`HTTPException` adalah *exception* biasa milik FastAPI. Dengan `raise`, eksekusi fungsi berhenti dan klien menerima status dan `detail` yang kamu tentukan. Cara kerjanya dibahas lengkap di Modul 04; di sini cukup dipakai untuk kasus "tidak ditemukan".

### Buat tugas

```python
@app.post("/tugas", response_model=Tugas, status_code=201)
def buat_tugas(data: TugasInput):
    global id_berikutnya
    tugas = Tugas(id=id_berikutnya, **data.model_dump())
    tugas_db[tugas.id] = tugas
    id_berikutnya += 1
    return tugas
```

- `data: TugasInput` dibaca dari body dan divalidasi otomatis.
- `global` diperlukan karena fungsi mengubah variabel `id_berikutnya` di luar fungsi.
- `**data.model_dump()` meneruskan semua field `data` sebagai argumen bernama untuk `Tugas`.

### Daftar tugas dengan filter dan paginasi

```python
hasil = list(tugas_db.values())
if selesai is not None:
    hasil = [t for t in hasil if t.selesai == selesai]
if cari is not None:
    hasil = [t for t in hasil if cari.lower() in t.judul.lower()]
awal = (halaman - 1) * batas
return hasil[awal : awal + batas]
```

Filter diterapkan hanya bila parameternya dikirim. **Paginasi** memotong daftar menjadi halaman: `halaman=2&batas=1` melewati 1 tugas lalu mengambil 1. Parameter `halaman` dan `batas` dibatasi dengan `Query` seperti di [Validasi Path dan Query Parameter](validasi-path-query.md).

### Ambil satu, ganti, dan hapus

```python
@app.put("/tugas/{tugas_id}", response_model=Tugas)
def ganti_tugas(tugas_id: IdTugas, data: TugasInput):
    cari_tugas(tugas_id)
    tugas = Tugas(id=tugas_id, **data.model_dump())
    tugas_db[tugas_id] = tugas
    return tugas
```

`PUT` **mengganti seluruh** tugas, jadi field yang tidak dikirim kembali ke nilai default (teruji di bawah). Pemanggilan `cari_tugas` di awal memastikan tugasnya ada, kalau tidak langsung `404`. `DELETE` bekerja serupa lalu menghapus data dan menjawab `204 No Content`, yaitu sukses tanpa isi.

## Menjalankan

Siapkan venv seperti di [Instalasi dan Virtual Environment](../01-pengenalan/instalasi-dan-venv.md), lalu:

```powershell
fastapi dev main.py
```

Server berjalan di `http://127.0.0.1:8000`. Coba juga `/docs`.

## Mencoba request

Simpan tiga file JSON berikut di folder yang sama:

```json title="tugas1.json"
{"judul":"Belajar FastAPI","catatan":"Modul 03","prioritas":1}
```

```json title="tugas2.json"
{"judul":"Cuci motor"}
```

```json title="ganti.json"
{"judul":"Belajar FastAPI","prioritas":1,"selesai":true}
```

Semua hasil di bawah berasal dari server `fastapi dev` yang dijalankan berurutan dari keadaan kosong.

### Buat tugas

```powershell
curl.exe -i -X POST http://127.0.0.1:8000/tugas -H "Content-Type: application/json" -d "@tugas1.json"
```

Status `HTTP/1.1 201 Created`, isi:

```json
{"judul":"Belajar FastAPI","catatan":"Modul 03","prioritas":1,"selesai":false,"id":1}
```

Tugas kedua (`tugas2.json`) menerima nilai default dan `id` 2:

```json
{"judul":"Cuci motor","catatan":null,"prioritas":2,"selesai":false,"id":2}
```

### Daftar, filter, dan paginasi

```powershell
curl.exe "http://127.0.0.1:8000/tugas?cari=motor"
```

```json
[{"judul":"Cuci motor","catatan":null,"prioritas":2,"selesai":false,"id":2}]
```

| Request | Hasil |
|---|---|
| `GET /tugas` | kedua tugas |
| `GET /tugas?selesai=true` | `[]` (belum ada yang selesai) |
| `GET /tugas?batas=1&halaman=2` | hanya tugas `id` 2 |

### Ambil satu dan tidak ditemukan

```powershell
curl.exe -i http://127.0.0.1:8000/tugas/99
```

```text
HTTP/1.1 404 Not Found
{"detail":"Tugas tidak ditemukan"}
```

### Ganti tugas

```powershell
curl.exe -X PUT http://127.0.0.1:8000/tugas/1 -H "Content-Type: application/json" -d "@ganti.json"
```

```json
{"judul":"Belajar FastAPI","catatan":null,"prioritas":1,"selesai":true,"id":1}
```

Perhatikan `catatan` kembali `null` karena tidak ikut dikirim. Itulah sifat `PUT`.

### Hapus tugas

```powershell
curl.exe -i -X DELETE http://127.0.0.1:8000/tugas/2
```

Status `HTTP/1.1 204 No Content`. Meminta `/tugas/2` lagi menghasilkan `404` yang sama seperti di atas, dan `GET /tugas?selesai=true` kini berisi tugas `id` 1 yang sudah selesai.

### Data tidak valid

Body `{"judul":"ab","prioritas":5}` dikirim ke `POST /tugas`:

```json
{"detail":[{"type":"string_too_short","loc":["body","judul"],"msg":"String should have at least 3 characters","input":"ab","ctx":{"min_length":3}},{"type":"less_than_equal","loc":["body","prioritas"],"msg":"Input should be less than or equal to 3","input":5,"ctx":{"le":3}}]}
```

Dua pelanggaran dilaporkan sekaligus, dengan `422`. Path `GET /tugas/0` juga ditolak dengan `422` (`greater_than_equal`, `loc` `["path","tugas_id"]`).

!!! warning "Keterbatasan tahap 1"
    - Data hilang saat server dimulai ulang (dalam memori). Tidak diuji dengan memulai ulang server.
    - Tidak ada pengamanan untuk akses bersamaan dan tidak ada pengguna atau login.
    - Tampilan Swagger UI belum diverifikasi lewat browser.

    Keterbatasan ini ditangani di tahap berikutnya.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Lupa `global id_berikutnya` | Python mengira variabel itu lokal sehingga muncul error saat dijalankan (perilaku Python; tidak dijalankan di sini). |
| Memakai satu model untuk input dan output | Klien bisa ikut mengirim `id`; pisahkan seperti `TugasInput` dan `Tugas`. |
| Menaruh route tetap setelah `/tugas/{tugas_id}` | Route dinamis menangkapnya lebih dulu. Lihat [Urutan Route](../02-dasar-routing/urutan-route.md). |
| Lupa memeriksa keberadaan data sebelum `del` | Terjadi `KeyError` dan klien menerima `500`, bukan `404`. Tidak dijalankan di sini. |
| Mengira data bertahan setelah server mati | Dalam memori, jadi hilang. |

## Latihan

1. **Dasar.** Tambahkan `GET /tugas/ringkasan` yang mengembalikan jumlah `total`, `selesai`, dan `belum`. Di mana kamu menaruhnya, dan mengapa?
2. **Filter.** Tambahkan filter `prioritas` pada `GET /tugas`.
3. **Endpoint baru.** Buat `PATCH /tugas/{tugas_id}/selesai` yang menandai tugas selesai. Apa responsnya untuk ID yang tidak ada?
4. **Analisis.** Setelah tugas 2 dihapus, ID berapa yang diterima tugas berikutnya? Mengapa ID tidak dipakai ulang?

??? success "Kunci jawaban"
    Jawaban 1 sampai 3 dijalankan dengan `TestClient` pada aplikasi yang route barunya ditaruh sebelum route lama. Jawaban 4 adalah penalaran dari kode, tidak dijalankan.

    ```python
    @app.get("/tugas/ringkasan")  # harus sebelum /tugas/{tugas_id}
    def ringkasan():
        total = len(tugas_db)
        selesai = sum(t.selesai for t in tugas_db.values())
        return {"total": total, "selesai": selesai, "belum": total - selesai}


    # tambahan parameter pada daftar_tugas: prioritas: int | None = None
    # lalu di badan fungsi:
    #     if prioritas is not None:
    #         hasil = [t for t in hasil if t.prioritas == prioritas]


    @app.patch("/tugas/{tugas_id}/selesai", response_model=Tugas)
    def tandai_selesai(tugas_id: IdTugas):
        tugas = cari_tugas(tugas_id)
        tugas.selesai = True
        return tugas
    ```

    1. Taruh **sebelum** `/tugas/{tugas_id}`. Hasil uji: `{"total":2,"selesai":0,"belum":2}`, dan setelah satu tugas ditandai selesai: `{"total":2,"selesai":1,"belum":1}`.
    2. `?prioritas=1` hanya mengembalikan tugas berprioritas 1 (teruji).
    3. Tugas yang ada menjadi `selesai: true`. ID yang tidak ada menghasilkan `404` dengan `{"detail":"Tugas tidak ditemukan"}` (teruji).
    4. ID berikutnya adalah 3, bukan 2: `id_berikutnya` hanya bertambah dan tidak pernah turun. Dengan begitu ID lama tidak menunjuk ke data yang berbeda.

## Ringkasan

- Proyek tahap 1 menggabungkan semua materi Modul 03 menjadi CRUD dalam memori.
- Model input (`TugasInput`) dan model output (`Tugas`) dipisah; `id` dibuat oleh server.
- Data disimpan di `dict` dengan ID sebagai kunci; ID bertambah lewat penghitung.
- `GET` daftar mendukung filter dan paginasi lewat query parameter yang divalidasi.
- `PUT` mengganti seluruh data; `DELETE` menjawab `204`; data tidak ada menghasilkan `404` lewat `HTTPException`.
- Tahap berikutnya menambah penanganan error yang terstruktur (Modul 04) dan penyimpanan di basis data (Modul 06).

## Langkah berikutnya

Kembali ke [Modul 03: Data dan Validasi](index.md). Materi berikutnya ada di Modul 04: Penanganan Error.
