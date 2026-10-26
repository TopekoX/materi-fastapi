# Path Parameter

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan apa itu path parameter dan kapan memakainya.
- [ ] Menulis endpoint dengan path parameter dan memberinya tipe data.
- [ ] Menjelaskan bagaimana FastAPI mengonversi dan memvalidasi nilai path parameter.
- [ ] Membaca response error `422` dan menemukan penyebabnya.
- [ ] Memakai lebih dari satu path parameter dalam satu endpoint.

## Prasyarat

- Sudah menyelesaikan [Modul 01: Pengenalan](../01-pengenalan/index.md), terutama [Endpoint Pertama](../01-pengenalan/endpoint-pertama.md) dan [HTTP dan REST](../01-pengenalan/http-dan-rest.md).
- Type hints dasar di Python, misalnya `nama: str` dan `umur: int`.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7** dan **FastAPI 0.162.0** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Di [HTTP dan REST](../01-pengenalan/http-dan-rest.md), endpoint untuk satu tugas ditulis dengan path tetap, yaitu `/tugas/1`. Itu hanya melayani tugas nomor 1. Jika ada seratus tugas, kamu tidak mungkin menulis seratus endpoint.

Solusinya adalah **path parameter**: bagian dari path yang nilainya boleh berubah. Kamu menandainya dengan kurung kurawal:

```text
/tugas/{tugas_id}
        └── bagian yang berubah

/tugas/1      → tugas_id = 1
/tugas/42     → tugas_id = 42
```

Satu endpoint kini melayani semua nomor tugas. Nilai yang dikirim klien pada bagian itu diteruskan ke fungsimu sebagai argumen.

Path parameter cocok untuk **mengidentifikasi sumber daya tertentu**, misalnya tugas nomor tertentu atau pengguna dengan ID tertentu. Untuk opsi tambahan seperti pencarian atau pengurutan, dipakai query parameter pada materi berikutnya di modul ini.

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/02-dasar-routing/path-parameter/main.py"
```

## Penjelasan kode

### Menandai bagian yang berubah

```python
@app.get("/tugas/{tugas_id}")
```

Kurung kurawal berisi **nama** path parameter, yaitu `tugas_id`. Nama ini bebas, tetapi harus sama persis dengan nama argumen pada fungsi.

### Menerima nilainya di fungsi

```python
def detail_tugas(tugas_id: int):
    return {"tugas_id": tugas_id, "tipe": type(tugas_id).__name__}
```

| Bagian | Fungsinya |
|---|---|
| `tugas_id` | Argumen dengan nama yang sama seperti di kurung kurawal. FastAPI mengisinya dengan nilai dari URL |
| `: int` | *Type hint*. Memerintahkan FastAPI mengubah nilai menjadi bilangan bulat dan menolak nilai yang bukan bilangan bulat |
| `type(tugas_id).__name__` | Hanya untuk contoh: menampilkan nama tipe nilai yang diterima, agar kamu bisa melihat hasil konversinya |

### Path parameter bertipe teks

```python
@app.get("/salam/{nama}")
def salam(nama: str):
    return {"pesan": f"Halo, {nama}!"}
```

Tipe `str` berarti nilainya diterima apa adanya sebagai teks. Bentuk `f"Halo, {nama}!"` adalah *f-string* Python yang menyisipkan nilai `nama` ke dalam teks. Kurung kurawal di f-string tidak berhubungan dengan kurung kurawal di path.

### Hubungan antarbagian

```text
Request  : GET /tugas/3
              │  FastAPI mencocokkan dengan "/tugas/{tugas_id}"
              ▼
Konversi : teks "3" → bilangan bulat 3  (karena tugas_id: int)
              ▼
Fungsi   : detail_tugas(tugas_id=3)
              ▼
Response : {"tugas_id":3,"tipe":"int"}
```

## Menjalankan aplikasi

Pastikan venv aktif, lalu dari folder `main.py`:

```bash
fastapi dev main.py
```

Cara menjalankan dan membaca log dibahas di [Menjalankan Server](../01-pengenalan/menjalankan-server.md). Contoh di bawah memakai port `8000`; sesuaikan bila kamu memakai port lain.

## Mencoba request

Gunakan terminal kedua (pengguna PowerShell: ketik `curl.exe`) atau address bar browser:

```bash
curl -i http://127.0.0.1:8000/tugas/3
curl -i http://127.0.0.1:8000/salam/Budi
```

Hasil dari eksekusi nyata:

| Request | Status | Body |
|---|---|---|
| `GET /tugas/3` | `200 OK` | `{"tugas_id":3,"tipe":"int"}` |
| `GET /salam/Budi` | `200 OK` | `{"pesan":"Halo, Budi!"}` |
| `GET /salam/123` | `200 OK` | `{"pesan":"Halo, 123!"}` |
| `GET /tugas/-5` | `200 OK` | `{"tugas_id":-5,"tipe":"int"}` |
| `GET /tugas/007` | `200 OK` | `{"tugas_id":7,"tipe":"int"}` |
| `GET /salam/Budi%20Santoso` | `200 OK` | `{"pesan":"Halo, Budi Santoso!"}` |

Beberapa hal yang bisa diamati:

- Nilai `3` pada URL adalah teks. Berkat `: int`, fungsi menerimanya sebagai bilangan bulat; kolom `tipe` membuktikannya.
- Bilangan negatif dan `007` diterima sebagai bilangan bulat; `007` menjadi `7`.
- Spasi pada URL ditulis sebagai `%20`. FastAPI mengubahnya kembali menjadi spasi sebelum diteruskan ke fungsi.

### Konversi dan validasi

Tipe pada path parameter punya dua fungsi: **konversi** (mengubah teks menjadi tipe yang diminta) dan **validasi** (menolak nilai yang tidak bisa diubah). Pydantic yang mengerjakan validasinya, seperti dijelaskan di [Apa itu FastAPI](../01-pengenalan/apa-itu-fastapi.md).

Coba nilai yang bukan bilangan bulat:

```bash
curl -i http://127.0.0.1:8000/tugas/abc
```

Hasil nyata:

```text
HTTP/1.1 422 Unprocessable Content
```

```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["path", "tugas_id"],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "abc"
    }
  ]
}
```

(Pada pengujian, body dikirim dalam satu baris tanpa spasi; di sini diformat agar mudah dibaca.)

Cara membaca error ini:

| Bidang | Artinya |
|---|---|
| `type` | Jenis kesalahan: `int_parsing`, gagal diubah menjadi bilangan bulat |
| `loc` | Lokasi kesalahan: parameter `tugas_id` di bagian `path` |
| `msg` | Penjelasan kesalahan |
| `input` | Nilai yang dikirim klien |

Status `422` berarti request dimengerti, tetapi isinya tidak valid. Perhatikan bahwa kamu tidak menulis kode pemeriksaan sama sekali: cukup dengan `: int`.

Nilai desimal ditolak dengan cara yang sama: `GET /tugas/1.5` mengembalikan `422` dengan `input` `"1.5"`.

### Dokumentasi otomatis

Tipe yang kamu tulis juga masuk ke dokumentasi. Pada pengujian, `/openapi.json` mencatat parameter `tugas_id` dengan `in: path`, `required: true`, dan tipe `integer`, serta daftar response `200` dan `422`. Cara membaca dokumentasi ini dibahas di [Dokumentasi Interaktif](../01-pengenalan/dokumentasi-interaktif.md).

## Variasi

### Tipe lain

Selain `int` dan `str`, tipe `float` juga bisa dipakai. Pada pengujian dengan `jumlah: float`, `GET /harga/4.5` menghasilkan `{"jumlah":4.5,"tipe":"float"}`, sedangkan `GET /harga/abc` menghasilkan `422` dengan `type` `float_parsing`.

### Tanpa type hint

Jika tipe tidak ditulis, nilai tetap berupa teks. Pada pengujian, `GET /tanpa-tipe/5` untuk fungsi `def tanpa_tipe(nilai)` menghasilkan `{"nilai":"5","tipe":"str"}`: angka `5` diterima sebagai teks `"5"`. Karena itu tulislah tipenya agar konversi dan validasi bekerja.

### Lebih dari satu path parameter

Satu path boleh berisi beberapa parameter:

```python
@app.get("/pengguna/{pengguna_id}/tugas/{tugas_id}")
def tugas_pengguna(pengguna_id: int, tugas_id: int):
    return {"pengguna_id": pengguna_id, "tugas_id": tugas_id}
```

Pada pengujian, `GET /pengguna/2/tugas/9` menghasilkan `{"pengguna_id":2,"tugas_id":9}`. Jika salah satunya tidak valid, misalnya `/pengguna/2/tugas/x`, hasilnya `422` dengan `loc` `["path","tugas_id"]`: error menunjuk parameter yang bermasalah.

## Kesalahan umum

Semua kasus berikut dijalankan dan dicatat apa adanya.

### 1. Nilai tidak sesuai tipe (`422`)

`GET /tugas/abc` mengembalikan `422`. **Solusi:** kirim nilai yang sesuai tipe, atau baca bidang `loc` dan `input` pada error untuk menemukan parameter dan nilai yang salah.

### 2. Nama di path berbeda dengan nama argumen

Jika path-nya `/salah/{id_tugas}` tetapi fungsinya `def nama_beda(tugas_id: int)`, pada pengujian `GET /salah/1` mengembalikan `422`, dengan error:

```json
{"detail":[{"type":"missing","loc":["query","tugas_id"],"msg":"Field required","input":null}]}
```

Perhatikan `loc`-nya: `query`, bukan `path`. Karena `tugas_id` tidak ada di path, FastAPI menganggapnya sebagai query parameter yang wajib diisi. **Solusi:** samakan nama di path dan di argumen fungsi. Query parameter dibahas di materi berikutnya.

### 3. Nilai kosong

`GET /salam/` (tanpa nama) mengembalikan `404 Not Found` dengan `{"detail":"Not Found"}`. Pada pengujian, `GET /tugas/` juga `404`, begitu pula `GET /tugas` tanpa garis miring dan tanpa nomor. Path parameter harus terisi agar endpoint cocok. **Solusi:** sertakan nilainya, mis. `/salam/Budi`.

### 4. Nilai mengandung garis miring

`GET /salam/a/b` mengembalikan `404`. Garis miring memisahkan bagian path, jadi `a/b` dibaca sebagai dua bagian, bukan satu nilai. **Solusi:** untuk nilai dengan garis miring, pertimbangkan menggunakan query parameter; FastAPI juga punya cara khusus untuk path parameter berisi path, yang tidak dibahas di sini dan belum saya uji.

## Latihan

1. **Dasar.** Tambahkan endpoint `GET /kota/{nama_kota}` yang mengembalikan `{"kota": "<nama_kota>"}`. Panggil `/kota/Makassar`.
2. **Menengah.** Tambahkan endpoint `GET /harga/{jumlah}` dengan `jumlah: float`. Coba `4.5` dan `abc`, lalu bandingkan statusnya.
3. **Menengah.** Buat `GET /pengguna/{pengguna_id}/tugas/{tugas_id}` dan kirim `/pengguna/2/tugas/x`. Dari bidang `loc`, parameter mana yang salah?
4. **Tantangan.** Perbaiki endpoint berikut agar `GET /salah/1` mengembalikan `200`, lalu jelaskan penyebab `422` sebelumnya:

    ```python
    @app.get("/salah/{id_tugas}")
    def nama_beda(tugas_id: int):
        return {"tugas_id": tugas_id}
    ```

??? success "Kunci jawaban"
    1. Kode:

        ```python
        @app.get("/kota/{nama_kota}")
        def kota(nama_kota: str):
            return {"kota": nama_kota}
        ```

        `GET /kota/Makassar` menghasilkan `{"kota":"Makassar"}`.
    2. `GET /harga/4.5` menghasilkan `200`, `GET /harga/abc` menghasilkan `422`.
    3. Parameter `tugas_id` (`loc` berisi `["path","tugas_id"]`).
    4. Samakan nama: ganti argumen menjadi `id_tugas`, yaitu `def nama_beda(id_tugas: int): return {"tugas_id": id_tugas}`. Penyebab `422`: nama `tugas_id` tidak ada di path, jadi dibaca sebagai query parameter wajib yang tidak dikirim.

    Jawaban 1 dan 4 diuji dengan `TestClient` dari FastAPI, bukan lewat browser atau `curl`.

## Ringkasan

- Path parameter adalah bagian path yang nilainya berubah, ditulis dengan kurung kurawal, mis. `/tugas/{tugas_id}`.
- Nama di kurung kurawal harus sama dengan nama argumen fungsi.
- Type hint pada argumen (mis. `: int`) membuat FastAPI mengonversi nilai dan menolak yang tidak valid dengan `422`.
- Tanpa type hint, nilai diterima sebagai teks.
- Error `422` memuat `type`, `loc`, `msg`, dan `input` yang menunjuk penyebabnya.
- Satu path dapat memiliki beberapa path parameter. Tipe yang ditulis ikut masuk ke dokumentasi otomatis.

## Langkah berikutnya

Kembali ke daftar materi di [Modul 02: Dasar Routing](index.md). Materi berikutnya adalah query parameter.
