# HTTP dan REST

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan alur *request* dan *response* pada HTTP.
- [ ] Membaca bagian-bagian request dan response: method, path, header, body, dan status code.
- [ ] Memilih HTTP method yang sesuai dengan tujuan sebuah endpoint.
- [ ] Menjelaskan apa itu REST dan menerapkannya pada penamaan endpoint.
- [ ] Membuktikan perilaku HTTP dengan memanggil API buatanmu lewat `curl`.

## Prasyarat

- Sudah membaca [Apa itu FastAPI](apa-itu-fastapi.md) dan [Endpoint Pertama](endpoint-pertama.md).
- Lingkungan kerja (virtual environment dan FastAPI) sudah siap seperti di [bagian persiapan](endpoint-pertama.md#persiapan).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7** dan **FastAPI 0.162.0** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi atau sistem operasi lain **belum diuji**.

## HTTP: aturan percakapan klien dan server

**HTTP** (*HyperText Transfer Protocol*) adalah aturan yang disepakati klien dan server tentang cara bertukar pesan di web. Polanya sederhana:

1. Klien mengirim satu **request**.
2. Server membalas dengan satu **response**.

Klien selalu yang memulai. Server tidak mengirim apa pun sebelum ada request.

Dengan memahami HTTP, kamu tahu persis apa yang dikirim dan diterima API-mu. Pengetahuan ini dipakai di setiap modul berikutnya, termasuk saat mencari tahu mengapa sebuah request gagal.

### Anatomi request

Sebuah request terdiri dari beberapa bagian:

| Bagian | Fungsinya |
|---|---|
| **Method** | Tindakan yang diminta, misalnya `GET` |
| **Path** | Alamat sumber daya yang diminta, misalnya `/tugas` |
| **Header** | Keterangan tambahan tentang request, berupa pasangan nama dan nilai |
| **Body** | Data yang dikirim ke server. Bersifat opsional |

Request `GET` ke API pada halaman ini terlihat seperti berikut. Teks ini diambil dari `curl -v` dan hanya menyisakan baris request:

```http
GET /tugas HTTP/1.1
Host: 127.0.0.1:8767
User-Agent: curl/8.11.0
Accept: */*
```

Baris pertama berisi method (`GET`), path (`/tugas`), dan versi HTTP. Baris berikutnya adalah header. Nomor port `8767` dan versi `curl` akan berbeda pada komputermu. Request ini tidak memiliki body.

### Anatomi response

Response juga memiliki bagian-bagian:

| Bagian | Fungsinya |
|---|---|
| **Status code** | Angka yang menyatakan hasil request, disertai teks singkat |
| **Header** | Keterangan tambahan tentang response |
| **Body** | Isi balasan, misalnya data JSON |

Response dari request di atas, juga dari eksekusi nyata:

```http
HTTP/1.1 200 OK
date: Mon, 26 Oct 2026 03:26:36 GMT
server: uvicorn
content-length: 33
content-type: application/json

{"aksi":"mengambil daftar tugas"}
```

Baris pertama memuat status code `200` dan teks `OK`. Header `content-type: application/json` memberi tahu klien bahwa body berformat JSON, dan `content-length` adalah ukuran body dalam byte. Setelah baris kosong, barulah body ditampilkan.

### Status code

Status code dikelompokkan berdasarkan angka pertamanya:

| Kelompok | Arti umum | Yang muncul di halaman ini |
|---|---|---|
| `2xx` | Berhasil | `200 OK`, `201 Created` |
| `3xx` | Pengalihan ke alamat lain | `307 Temporary Redirect` |
| `4xx` | Kesalahan ada pada request klien | `404 Not Found`, `405 Method Not Allowed` |
| `5xx` | Kesalahan terjadi di server | Tidak muncul di sini |

Dengan kelompok ini, kamu sudah bisa menebak arti sebuah status code yang belum pernah kamu lihat.

### HTTP method

Method menyatakan tujuan request. Kelima method berikut paling sering dipakai pada API:

| Method | Tujuan umum |
|---|---|
| `GET` | Mengambil data |
| `POST` | Membuat data baru |
| `PUT` | Mengganti data yang sudah ada |
| `PATCH` | Mengubah sebagian data |
| `DELETE` | Menghapus data |

Tabel ini adalah kesepakatan umum. Server tidak dipaksa mengikutinya, sehingga disiplin penggunaannya ada pada pembuat API.

### JSON

**JSON** adalah format teks untuk menuliskan data, yang bentuknya mirip `dict` dan `list` di Python. Pada [Endpoint Pertama](endpoint-pertama.md) kamu sudah melihat FastAPI mengubah `dict` menjadi JSON secara otomatis.

## REST: cara merancang API yang rapi

**REST** adalah gaya perancangan API di atas HTTP. REST bukan library dan bukan standar yang diperiksa otomatis. FastAPI tidak memaksamu mengikutinya, tetapi API yang mengikutinya lebih mudah ditebak dan dipakai.

Ide dasarnya:

- **Resource**: segala sesuatu yang dikelola API dipandang sebagai sumber daya, misalnya tugas. Setiap resource punya path.
- **Path memakai kata benda**, bukan kata kerja. Gunakan `/tugas`, bukan `/ambil-tugas`.
- **Method menyatakan aksinya**. Path yang sama bisa dipakai oleh beberapa method.
- **Tiap request berdiri sendiri**: server tidak bergantung pada request sebelumnya untuk memahami request yang sedang masuk.
- **Representasi data**: resource dikirim dalam format tertentu, biasanya JSON.

Penerapannya pada resource `tugas`:

| Tujuan | Method | Path |
|---|---|---|
| Mengambil daftar tugas | `GET` | `/tugas` |
| Membuat tugas baru | `POST` | `/tugas` |
| Mengambil satu tugas | `GET` | `/tugas/1` |
| Mengganti satu tugas | `PUT` | `/tugas/1` |
| Menghapus satu tugas | `DELETE` | `/tugas/1` |

Perhatikan bahwa `/tugas` dipakai dua kali dengan method berbeda, begitu pula `/tugas/1`. Angka `1` adalah nomor tugas. Pada contoh ini nomornya ditulis tetap; cara membuatnya berubah-ubah dibahas di [Path Parameter](../02-dasar-routing/path-parameter.md).

## Kode lengkap

Kode berikut mengimplementasikan tabel di atas. Simpan sebagai `main.py` di folder kerja:

```python title="main.py"
--8<-- "fastapi/01-pengenalan/http-dan-rest/main.py"
```

!!! warning "Hanya contoh"
    Endpoint ini tidak menyimpan atau mengubah data apa pun. Setiap endpoint hanya mengembalikan teks yang menjelaskan aksinya, supaya kamu bisa fokus pada method dan status code. Penyimpanan data baru dibahas di modul berikutnya.

## Penjelasan kode

### Impor dan aplikasi

```python
from fastapi import FastAPI

app = FastAPI()
```

Sama seperti di [Endpoint Pertama](endpoint-pertama.md#penjelasan-kode): membuat objek aplikasi yang akan menampung semua endpoint.

### Satu path, dua method

```python
@app.get("/tugas")
def daftar_tugas():
    return {"aksi": "mengambil daftar tugas"}


@app.post("/tugas", status_code=201)
def buat_tugas():
    return {"aksi": "membuat tugas baru"}
```

Dua endpoint ini memakai path `/tugas` yang sama. Yang membedakannya adalah method pada decorator: `@app.get` untuk `GET`, dan `@app.post` untuk `POST`. FastAPI memilih fungsi berdasarkan pasangan method dan path.

Parameter `status_code=201` pada `@app.post` menentukan status code response ketika berhasil. Tanpa parameter ini, endpoint mengembalikan `200`. Kode `201 Created` lazim dipakai untuk menandakan bahwa sesuatu berhasil dibuat.

### Endpoint untuk satu tugas

```python
@app.get("/tugas/1")
def detail_tugas():
    return {"aksi": "mengambil tugas nomor 1"}


@app.put("/tugas/1")
def ganti_tugas():
    return {"aksi": "mengganti tugas nomor 1"}


@app.delete("/tugas/1")
def hapus_tugas():
    return {"aksi": "menghapus tugas nomor 1"}
```

Tiga endpoint ini berbagi path `/tugas/1` dan dibedakan oleh method: `get`, `put`, dan `delete`. Karena path-nya tertulis tetap, hanya tugas nomor 1 yang ada pada contoh ini.

### Hubungan antarbagian

```text
Request  : POST /tugas
             │  FastAPI mencocokkan method + path
             ▼
Fungsi   : buat_tugas()  → mengembalikan {"aksi": "membuat tugas baru"}
             │  FastAPI menambahkan status_code=201
             ▼
Response : 201 Created + body JSON
```

## Menjalankan aplikasi

Langkah persiapan sama dengan di [Endpoint Pertama](endpoint-pertama.md#persiapan). Pastikan virtual environment aktif, lalu jalankan dari folder yang berisi `main.py`:

```bash
fastapi dev main.py
```

Alamat server tampil di log. Contoh di bawah memakai `http://127.0.0.1:8000`. Jika port tersebut sudah dipakai, tambahkan `--port` dan sesuaikan alamatnya.

## Mencoba request

Browser hanya mengirim `GET` saat kamu mengetik alamat di address bar, sehingga untuk method lain dipakai `curl`. Jalankan di terminal kedua (pengguna PowerShell: ketik `curl.exe`, bukan `curl`):

```bash
curl -i http://127.0.0.1:8000/tugas
curl -i -X POST http://127.0.0.1:8000/tugas
curl -i -X PUT http://127.0.0.1:8000/tugas/1
curl -i -X DELETE http://127.0.0.1:8000/tugas/1
```

| Opsi | Artinya |
|---|---|
| `-i` | Tampilkan status line dan header response, bukan hanya body |
| `-X <METHOD>` | Pakai method tersebut. Tanpa `-X`, `curl` memakai `GET` |

### Hasil yang diharapkan

Hasil berikut berasal dari eksekusi nyata:

| Request | Status | Body |
|---|---|---|
| `GET /tugas` | `200 OK` | `{"aksi":"mengambil daftar tugas"}` |
| `POST /tugas` | `201 Created` | `{"aksi":"membuat tugas baru"}` |
| `GET /tugas/1` | `200 OK` | `{"aksi":"mengambil tugas nomor 1"}` |
| `PUT /tugas/1` | `200 OK` | `{"aksi":"mengganti tugas nomor 1"}` |
| `DELETE /tugas/1` | `200 OK` | `{"aksi":"menghapus tugas nomor 1"}` |

Semua response berheader `content-type: application/json`. Perhatikan bahwa `POST` menghasilkan `201`, sedangkan yang lain `200`, sesuai `status_code=201` pada kode.

Di `http://127.0.0.1:8000/docs` kelima endpoint ini juga tercantum beserta method-nya. Daftar method per path di `/openapi.json` hasil eksekusi adalah `/tugas`: `get`, `post`; `/tugas/1`: `delete`, `get`, `put`. Tampilan `/docs` di browser belum saya lihat langsung.

## Kesalahan umum

Semua kasus berikut dijalankan dan dicatat apa adanya.

### 1. Method tidak didukung path itu (`405`)

```bash
curl -i -X DELETE http://127.0.0.1:8000/tugas
```

Hasilnya `405 Method Not Allowed` dengan body `{"detail":"Method Not Allowed"}`. Path `/tugas` ada, tetapi tidak punya endpoint `DELETE`. **Solusi:** gunakan method yang terdaftar, atau lihat daftar endpoint di `/docs`.

!!! note "Header `allow`"
    Response `405` di atas memuat header `allow: GET`. Padahal `/tugas` juga mendukung `POST`. Jadi header ini tidak boleh dijadikan satu-satunya rujukan; periksa juga `/docs`.

### 2. Nomor yang tidak terdaftar (`404`)

```bash
curl -i http://127.0.0.1:8000/tugas/2
```

Hasilnya `404 Not Found` dengan body `{"detail":"Not Found"}`. Pada contoh ini hanya `/tugas/1` yang didaftarkan. **Solusi:** pakai path yang ada. Untuk nomor yang bisa berubah, gunakan path parameter, seperti di [Path Parameter](../02-dasar-routing/path-parameter.md).

### 3. Garis miring di akhir path (`307`)

```bash
curl -i http://127.0.0.1:8000/tugas/1/
```

Hasilnya `307 Temporary Redirect` dengan header `location` yang menunjuk ke `/tugas/1` (tanpa garis miring akhir). `curl` tidak mengikuti pengalihan ini secara bawaan, sehingga yang tampil adalah response pengalihannya. **Solusi:** tulis path tanpa garis miring di akhir. Perilaku klien lain, misalnya browser, saat menerima pengalihan ini belum diuji.

!!! tip "Cara cepat membaca masalah"
    Lihat dulu angka pertama status code. `4xx` berarti periksa request-mu (method, path, data), `5xx` berarti periksa kode server.

## Latihan

1. **Dasar.** Pasangkan tujuan dengan method yang paling sesuai: (a) menghapus data, (b) mengambil data, (c) membuat data baru. Pilihan: `GET`, `POST`, `DELETE`.
2. **Menengah.** Jalankan `curl -i http://127.0.0.1:8000/tugas` dan tunjukkan mana yang termasuk status line, header, dan body pada output-nya.
3. **Menengah.** Tambahkan endpoint `PATCH /tugas/1` yang mengembalikan `{"aksi": "mengubah sebagian tugas nomor 1"}`, lalu panggil dengan `curl -i -X PATCH`.
4. **Tantangan.** Ubah `status_code` pada `POST /tugas` menjadi `202`, jalankan ulang, dan amati status line. Lalu jelaskan mengapa REST menganjurkan `/tugas` (kata benda) dan bukan `/buat-tugas`.

??? success "Kunci jawaban"
    1. (a) `DELETE`, (b) `GET`, (c) `POST`.
    2. Baris `HTTP/1.1 200 OK` adalah status line. Baris-baris berformat `nama: nilai` sampai baris kosong adalah header. Teks JSON setelah baris kosong adalah body.
    3. Tambahkan:

        ```python
        @app.patch("/tugas/1")
        def ubah_sebagian_tugas():
            return {"aksi": "mengubah sebagian tugas nomor 1"}
        ```

        Hasil yang teramati: status `200` dan body `{"aksi":"mengubah sebagian tugas nomor 1"}`.
    4. Ganti menjadi `@app.post("/tugas", status_code=202)`. Hasil yang teramati: status `202`, body tetap `{"aksi":"membuat tugas baru"}`. Alasan memakai kata benda: aksinya sudah dinyatakan oleh method (`POST`), sehingga path cukup menamai resource-nya dan bisa dipakai bersama method lain.

    Jawaban 3 dan 4 diuji dengan `TestClient` dari FastAPI, bukan lewat `curl`.

## Ringkasan

- HTTP adalah pola request dan response: klien meminta, server menjawab.
- Request terdiri dari method, path, header, dan body opsional. Response terdiri dari status code, header, dan body.
- Status code dikelompokkan: `2xx` berhasil, `3xx` pengalihan, `4xx` kesalahan klien, `5xx` kesalahan server.
- Method utama: `GET` mengambil, `POST` membuat, `PUT` mengganti, `PATCH` mengubah sebagian, `DELETE` menghapus.
- REST adalah gaya perancangan: path berupa kata benda untuk resource, dan method menyatakan aksinya.
- Di FastAPI, method ditentukan oleh decorator (`@app.get`, `@app.post`, dan seterusnya), dan status code sukses dapat diatur dengan `status_code`.

## Langkah berikutnya

Kembali ke daftar materi di [Modul 01: Pengenalan](index.md). Cara membuat path yang nilainya berubah-ubah dibahas di [Modul 02: Dasar Routing](../02-dasar-routing/index.md), mulai dari [Path Parameter](../02-dasar-routing/path-parameter.md).
