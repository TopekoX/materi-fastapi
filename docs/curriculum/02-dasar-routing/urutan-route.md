# Urutan Route

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan bagaimana FastAPI memilih endpoint untuk sebuah request.
- [ ] Menjelaskan mengapa path tetap harus didefinisikan sebelum path berparameter.
- [ ] Mengenali gejala urutan route yang salah, baik yang menghasilkan error maupun yang diam-diam salah.
- [ ] Menjelaskan peran HTTP method dalam pemilihan endpoint.
- [ ] Memperbaiki urutan route yang keliru.

## Prasyarat

- Sudah membaca [Path Parameter](path-parameter.md).
- Pernah menjalankan aplikasi FastAPI, seperti di [Menjalankan Server](../01-pengenalan/menjalankan-server.md).

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7** dan **FastAPI 0.162.0** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Aplikasi biasanya punya banyak endpoint. Saat sebuah request datang, FastAPI harus memilih satu endpoint yang akan menanganinya. Caranya sederhana: ia memeriksa endpoint **satu per satu, dari yang paling dulu kamu tulis**, dan memakai yang pertama cocok.

Biasanya tidak ada masalah, karena path yang berbeda tidak saling cocok. Masalah muncul ketika dua endpoint **bisa sama-sama cocok** dengan satu URL. Contohnya:

```text
/pengguna/saya            ← path tetap
/pengguna/{pengguna_id}   ← path berparameter

URL: /pengguna/saya
  cocok dengan keduanya!  (pada yang kedua, pengguna_id = "saya")
```

Dalam kasus itu, endpoint yang ditulis lebih dulu yang menang. Dokumentasi resmi FastAPI menyatakan hal yang sama: path tetap harus dideklarasikan sebelum path yang berparameter.

## Kode lengkap

Contoh ini punya dua file: urutan yang benar dan urutan yang sengaja dibalik, agar kamu bisa membandingkannya.

=== "Urutan benar (main.py)"

    ```python title="main.py"
    --8<-- "fastapi/02-dasar-routing/urutan-route/main.py"
    ```

=== "Urutan terbalik (main_salah.py)"

    ```python title="main_salah.py"
    --8<-- "fastapi/02-dasar-routing/urutan-route/main_salah.py"
    ```

## Penjelasan kode

### Dua endpoint yang bisa bentrok

```python
@app.get("/pengguna/saya")
def pengguna_saya():
    return {"pengguna": "pengguna yang sedang masuk"}


@app.get("/pengguna/{pengguna_id}")
def detail_pengguna(pengguna_id: int):
    return {"pengguna_id": pengguna_id}
```

| Endpoint | Artinya |
|---|---|
| `/pengguna/saya` | Path **tetap**: hanya cocok dengan tulisan `saya`. Maksudnya "pengguna yang sedang masuk" |
| `/pengguna/{pengguna_id}` | Path **berparameter**: cocok dengan nilai apa pun di bagian itu, termasuk `saya` |

Karena `saya` juga memenuhi `{pengguna_id}`, kedua endpoint bersaing untuk URL `/pengguna/saya`.

### Bedanya `main.py` dan `main_salah.py`

Isi kedua file **sama persis**. Satu-satunya perbedaan adalah urutan: `main.py` menulis path tetap dulu, `main_salah.py` menulis path berparameter dulu. Kode di `main_salah.py` terlihat wajar, dan itulah bahayanya.

### Hubungan antarbagian

```text
URL: GET /pengguna/saya

main.py:                                  main_salah.py:
 1. /pengguna/saya        ← cocok, dipakai   1. /pengguna/{pengguna_id} ← cocok, dipakai
 2. /pengguna/{pengguna_id}  (tidak dilihat)    2. /pengguna/saya          (tidak pernah tercapai)
```

## Menjalankan aplikasi

Jalankan salah satu file, atau keduanya di terminal terpisah dengan port berbeda:

```bash
fastapi dev main.py --port 8000
fastapi dev main_salah.py --port 8001
```

Cara kerja opsi `--port` ada di [Menjalankan Server](../01-pengenalan/menjalankan-server.md). Pastikan hanya ada satu server per port.

## Mencoba request

```bash
curl -i http://127.0.0.1:8000/pengguna/saya
curl -i http://127.0.0.1:8000/pengguna/5
curl -i http://127.0.0.1:8001/pengguna/saya
curl -i http://127.0.0.1:8001/pengguna/5
```

Hasil dari eksekusi nyata:

| File | Request | Status | Body |
|---|---|---|---|
| `main.py` | `GET /pengguna/saya` | `200 OK` | `{"pengguna":"pengguna yang sedang masuk"}` |
| `main.py` | `GET /pengguna/5` | `200 OK` | `{"pengguna_id":5}` |
| `main_salah.py` | `GET /pengguna/saya` | `422 Unprocessable Content` | error `int_parsing` |
| `main_salah.py` | `GET /pengguna/5` | `200 OK` | `{"pengguna_id":5}` |

Pada `main_salah.py`, request `/pengguna/saya` salah masuk ke endpoint `/pengguna/{pengguna_id}`. Di sana `saya` harus dikonversi menjadi bilangan bulat, dan gagal. Body error-nya:

```json
{"detail":[{"type":"int_parsing","loc":["path","pengguna_id"],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"saya"}]}
```

Perhatikan bahwa yang ditolak adalah `pengguna_id`, padahal kamu merasa memanggil `/pengguna/saya`. Itu petunjuk khas urutan yang salah. Log server juga mencatat `"GET /pengguna/saya HTTP/1.1" 422`.

Pada pengujian, FastAPI tidak mencoba endpoint berikutnya setelah endpoint pertama gagal validasi. Endpoint yang cocok dipilih lebih dulu, baru nilainya divalidasi.

### Salah yang tidak terlihat

Jika `pengguna_id` bertipe `str` (bukan `int`), tidak ada validasi yang gagal. Pada pengujian, dengan urutan terbalik:

```text
GET /pengguna/saya  →  200  {"pengguna_id":"saya"}
```

Hasilnya `200` tetapi **salah**: kamu mendapat "pengguna bernama saya", bukan "pengguna yang sedang masuk". Ini bentuk yang lebih berbahaya karena tidak ada pesan kesalahan apa pun.

## Peran HTTP method

Urutan hanya berpengaruh antara endpoint dengan **method yang sama**. Pada pengujian, `GET /pengguna/{pengguna_id}` didefinisikan lebih dulu, lalu `POST /pengguna/saya` sesudahnya:

| Request | Status | Body |
|---|---|---|
| `POST /pengguna/saya` | `200` | `{"post":"saya"}` |
| `GET /pengguna/saya` | `422` | error `int_parsing` |

`POST` tetap sampai ke endpoint `POST` yang benar, walaupun endpoint `GET` berparameter ada lebih dulu, karena method-nya tidak cocok dan dilewati. Hanya `GET` yang tersangkut. Jadi: **kedua syarat (path dan method) harus cocok** agar sebuah endpoint terpilih.

Urutan juga tidak berpengaruh bila path-nya memang tidak bisa saling cocok. Pada pengujian, `/a` dan `/b` bekerja benar dalam urutan apa pun.

## Aturan praktis

| Situasi | Yang harus dilakukan |
|---|---|
| Ada path tetap dan path berparameter yang bisa sama-sama cocok | Tulis **path tetap lebih dulu** |
| Path dan method sama-sama sama, ditulis dua kali | Hanya yang pertama dipakai; hapus duplikatnya |
| Path jelas berbeda | Urutan bebas |

## Kesalahan umum

Semua kasus berikut dijalankan dan dicatat apa adanya.

### 1. Path tetap ditulis setelah path berparameter

Gejala: `422` yang menyebut parameter dengan nilai yang seharusnya path tetap, seperti `input` `"saya"` di atas. **Solusi:** pindahkan endpoint path tetap ke atas endpoint berparameter.

### 2. Endpoint yang tidak pernah tercapai tanpa peringatan

Endpoint `/pengguna/saya` di `main_salah.py` tidak pernah dieksekusi, tetapi server tidak memberi peringatan apa pun saat dijalankan. Pada pengujian, dokumentasi otomatis (`/openapi.json`) tetap mendaftarkan keduanya, dalam urutan penulisan: `/pengguna/{pengguna_id}` lalu `/pengguna/saya`. Jadi dokumentasi tidak membantu menemukan masalah ini. **Pencegahan:** setiap kali menambah path tetap, periksa apakah ada path berparameter di atasnya yang bisa menimpanya.

### 3. Menulis path dan method yang sama dua kali

Pada pengujian, dua `@app.get("/halo")` menghasilkan `{"versi":"pertama"}` untuk `GET /halo`: hanya definisi pertama yang dipakai. Definisi kedua tidak pernah dijalankan, juga tanpa peringatan. **Solusi:** hapus atau ganti nama salah satunya.

### 4. Menganggap urutan selalu penting

Urutan hanya penting ketika dua endpoint dengan method sama bisa cocok dengan URL yang sama. Mengubah urutan `/a` dan `/b` tidak mengubah apa pun.

## Latihan

1. **Dasar.** Tanpa menjalankan, prediksikan hasil `GET /pengguna/saya` pada `main_salah.py` dan jelaskan alasannya. Lalu jalankan untuk membuktikan.
2. **Menengah.** Perbaiki `main_salah.py` agar `GET /pengguna/saya` mengembalikan `200`, tanpa mengubah isi fungsinya.
3. **Menengah.** Buat dua endpoint `GET /tugas/baru` (mengembalikan `{"aksi": "form tugas baru"}`) dan `GET /tugas/{tugas_id}` (`tugas_id: int`). Tulis dalam urutan yang benar, lalu uji `/tugas/baru` dan `/tugas/3`.
4. **Tantangan.** Jika `GET /pengguna/{pengguna_id}` ditulis lebih dulu dan `POST /pengguna/saya` ditulis sesudahnya, apa hasil `POST /pengguna/saya`? Jelaskan.

??? success "Kunci jawaban (sudah dijalankan)"
    1. Hasilnya `422` dengan `int_parsing`, karena `saya` dicocokkan lebih dulu dengan `/pengguna/{pengguna_id}` dan gagal menjadi bilangan bulat.
    2. Pindahkan blok `/pengguna/saya` ke atas blok `/pengguna/{pengguna_id}`. Hasilnya sama dengan `main.py`.
    3. Kode:

        ```python
        @app.get("/tugas/baru")
        def tugas_baru():
            return {"aksi": "form tugas baru"}


        @app.get("/tugas/{tugas_id}")
        def detail_tugas(tugas_id: int):
            return {"tugas_id": tugas_id}
        ```

        `/tugas/baru` menghasilkan `{"aksi":"form tugas baru"}` dan `/tugas/3` menghasilkan `{"tugas_id":3}`.
    4. Hasilnya `200` dengan `{"post":"saya"}` (teramati pada pengujian). Method `POST` tidak cocok dengan endpoint `GET`, jadi endpoint `GET` dilewati.

    Jawaban 3 diuji dengan `TestClient` dari FastAPI.

## Ringkasan

- FastAPI memeriksa endpoint berurutan sesuai urutan penulisan dan memakai yang pertama cocok.
- Path tetap harus ditulis **sebelum** path berparameter yang juga bisa cocok dengannya.
- Urutan yang salah bisa menghasilkan `422` yang membingungkan atau, bila parameter bertipe `str`, hasil `200` yang salah tanpa pesan kesalahan.
- Endpoint dipilih berdasarkan path **dan** method. Urutan hanya berpengaruh antar endpoint dengan method yang sama.
- Mendefinisikan path dan method yang sama dua kali membuat hanya definisi pertama yang dipakai.
- FastAPI tidak memperingatkan endpoint yang tidak pernah tercapai, jadi periksa urutan secara sadar.

## Langkah berikutnya

Kembali ke daftar materi di [Modul 02: Dasar Routing](index.md). Materi berikutnya adalah dasar async/await.
