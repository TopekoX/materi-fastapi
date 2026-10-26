# Dependency dengan yield

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan mengapa sebuah dependency perlu "membersihkan" sesuatu setelah request selesai.
- [ ] Menulis dependency dengan `yield` yang menyiapkan dan menutup sumber daya.
- [ ] Memakai `try` / `except` / `finally` di sekitar `yield` untuk menangani error.
- [ ] Menjelaskan urutan buka dan tutup pada dependency berantai yang memakai `yield`.
- [ ] Mengenali jebakan: tanpa `finally`, pembersihan terlewat saat terjadi error.

## Prasyarat

- Sudah membaca [Dependency Berantai](dependency-berantai.md).
- Sudah membaca [HTTPException](../04-penanganan-error/http-exception.md).
- Paham `try` / `except` / `finally` di Python.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7** dan **FastAPI 0.162.0** di Windows. Daftar lengkap versi ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**. Dokumentasi FastAPI mencatat bahwa perilaku dependency `yield` berkembang antar versi, jadi hasil di versi lain bisa berbeda.

## Konsep

Beberapa dependency membuka sesuatu yang harus **ditutup** setelah dipakai: koneksi basis data, berkas, atau transaksi. Dengan `return`, dependency hanya bisa menyerahkan nilai; tidak ada kesempatan membersihkannya.

Solusinya adalah `yield`. Menurut dokumentasi FastAPI:

- Kode **sebelum** `yield` dijalankan sebelum endpoint.
- Nilai yang di-`yield` diserahkan ke endpoint.
- Kode **sesudah** `yield` dijalankan setelah response selesai dikirim (perilaku bawaan).

Bayangkan meminjam buku: kamu mengambilnya (sebelum `yield`), membacanya (endpoint), lalu mengembalikannya (sesudah `yield`), apa pun yang terjadi saat membaca.

Aturan dasarnya: satu `yield` per dependency, dan dependency boleh `def` biasa atau `async def`.

Halaman ini memakai **sesi tiruan** sebagai pengganti basis data nyata. Koneksi basis data sungguhan baru dibahas di [Modul 06](../06-basis-data/index.md), tetapi pola `yield` yang dipelajari di sini persis yang akan dipakai di sana.

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/05-dependency-injection/dependency-yield/main.py"
```

## Penjelasan kode

### Daftar `log`

`log` adalah `list` global yang mencatat kejadian secara berurutan. Ini hanya alat percobaan agar urutan buka dan tutup terlihat; di kode nyata tidak diperlukan.

### Dependency pertama: koneksi

```python
def buka_koneksi():
    log.append("koneksi dibuka")
    try:
        yield "koneksi"
    finally:
        log.append("koneksi ditutup")
```

- Sebelum `yield`: "membuka" koneksi.
- `yield "koneksi"`: menyerahkan koneksi ke pihak yang membutuhkan.
- `finally`: dijalankan **apa pun hasilnya**, baik sukses maupun error. Itulah tempat yang tepat untuk menutup.

### Dependency kedua: transaksi, bergantung pada koneksi

```python
def transaksi(koneksi: Annotated[str, Depends(buka_koneksi)]):
    sesi = Sesi()
    log.append("transaksi mulai")
    try:
        yield sesi
        log.append("commit")
    except Exception:
        log.append("rollback")
        raise
    finally:
        log.append("transaksi selesai")
```

- `Depends(buka_koneksi)` menjadikan ini dependency berantai, seperti di halaman sebelumnya.
- `commit` berada tepat **setelah** `yield` di dalam `try`. Ia hanya tercapai bila endpoint selesai tanpa error.
- Bila endpoint (atau dependency lain) melempar exception, exception itu **dilemparkan kembali ke titik `yield`**, sehingga masuk ke blok `except` (dokumentasi FastAPI). Di sana kita mencatat `rollback`.
- `raise` tanpa argumen melempar ulang exception yang sama. Dokumentasi FastAPI menekankan: kecuali kamu sengaja melempar `HTTPException` atau sejenisnya, lempar ulang exception aslinya. Menelannya membuat klien menerima `500` tanpa jejak di log server.
- `finally` menutup transaksi, apa pun yang terjadi.

### Endpoint

```python
@app.post("/simpan/{nomor}")
def simpan(nomor: int, sesi: TransaksiDep):
    log.append(f"endpoint jalan ({nomor})")
    if nomor == 0:
        raise HTTPException(status_code=400, detail="Nomor tidak boleh 0")
    if nomor < 0:
        return 1 / 0
    sesi.data[nomor] = "tersimpan"
    return {"nomor": nomor, "status": "tersimpan"}
```

Endpoint menerima `sesi` (nilai yang di-`yield`). Tiga jalur sengaja disediakan: sukses, `HTTPException` (`nomor == 0`), dan exception tak terduga (`nomor < 0`, pembagian dengan nol).

## Menjalankan

```powershell
fastapi dev main.py
```

Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah.

## Mencoba request

Hasil di bawah dijalankan dengan `curl.exe`. Sebelum setiap percobaan, `POST /log/reset` mengosongkan `log`; setelahnya `GET /log` menampilkan isinya.

### Sukses

```powershell
curl.exe -X POST http://127.0.0.1:8000/simpan/5
```

```json
{"nomor":5,"status":"tersimpan"}
```

`GET /log`:

```json
["koneksi dibuka","transaksi mulai","endpoint jalan (5)","commit","transaksi selesai","koneksi ditutup"]
```

Urutan: koneksi dibuka → transaksi mulai → endpoint → commit → transaksi selesai → koneksi ditutup. Perhatikan penutupan dilakukan **terbalik**: yang dibuka terakhir ditutup duluan.

### `HTTPException` di endpoint

`POST /simpan/0` menghasilkan `400` dengan `{"detail":"Nomor tidak boleh 0"}`. Log-nya:

```json
["koneksi dibuka","transaksi mulai","endpoint jalan (0)","rollback","transaksi selesai","koneksi ditutup"]
```

`rollback` menggantikan `commit`, dan penutupan tetap terjadi.

### Exception tak terduga

`POST /simpan/-1` menghasilkan `500 Internal Server Error`, dengan log yang sama seperti kasus `HTTPException` (`rollback`, lalu transaksi dan koneksi ditutup). Terminal server mencatat `ZeroDivisionError`, karena kita melempar ulang dengan `raise`.

### Kegagalan validasi

`POST /simpan/abc` menghasilkan `422`. Log-nya:

```json
["koneksi dibuka","transaksi mulai","rollback","transaksi selesai","koneksi ditutup"]
```

Perhatikan: `endpoint jalan` tidak ada, tetapi dependency `yield` **sudah sempat dibuka dan di-rollback**. Pada pengujian ini, dependency dijalankan sebelum validasi path selesai dilaporkan. Jangan menaruh efek samping yang tidak bisa dibatalkan di bagian sebelum `yield`.

### Dokumentasi otomatis

Dependency `yield` tidak menambah parameter baru ke `/openapi.json`; hanya `nomor` yang tercatat untuk `/simpan/{nomor}`. Tampilan Swagger UI **belum diverifikasi** lewat browser.

## Kesalahan umum

Semua hasil di bawah diuji dengan `TestClient` pada endpoint yang melempar `HTTPException(400)`.

| Kesalahan | Akibat yang teramati |
|---|---|
| Menulis pembersihan sesudah `yield` tanpa `try` / `finally` | Pembersihan **terlewat** saat terjadi error: log hanya berisi `buka`, tanpa `tutup`. Pada request sukses, `tutup` tetap tercatat. |
| Memakai `try` / `finally`, tetapi lupa pembersihan di `finally` | Sama dengan di atas. Letakkan pembersihan di `finally`. |
| Menangkap exception di dependency lalu tidak melempar ulang (`except Exception: ...` tanpa `raise`) | Klien menerima `500 Internal Server Error`, dan log kustom hanya memuat `ditelan`. Padahal endpoint sebenarnya melempar `HTTPException(400)`. |
| Mengira `commit` selalu berjalan | `commit` hanya tercapai bila tidak ada exception. Lihat jalur `rollback` di atas. |
| Menaruh lebih dari satu `yield` dalam satu dependency | Dokumentasi FastAPI menyatakan hanya satu `yield` per dependency. Tidak dijalankan di sini. |
| Mengubah response dari kode sesudah `yield` | Response sudah terkirim; tidak bisa diubah. Dokumentasi FastAPI menjelaskan hal ini. |

## Latihan

1. **Dasar.** Tulis dependency `buka_berkas` yang mencatat `berkas dibuka` sebelum `yield` dan `berkas ditutup` di `finally`. Pakai di sebuah endpoint yang sukses. Apa isi log?
2. **Jebakan.** Ubah dependency itu menjadi tanpa `try` / `finally`, lalu buat endpoint melempar `HTTPException(400)`. Apa isi log dan apa status response?
3. **Prediksi.** Pada `main.py`, apa isi log dan status untuk `POST /simpan/3`, dibandingkan `POST /simpan/-1`?
4. **Analisis.** Mengapa `raise` setelah `rollback` penting?

??? success "Kunci jawaban"
    Jawaban 1 dan 2 dijalankan dengan `TestClient`; jawaban 3 mengacu pada hasil `curl` di atas; jawaban 4 adalah penalaran dari dokumentasi FastAPI dan hasil uji.

    ```python
    def buka_berkas():
        log.append("berkas dibuka")
        try:
            yield "berkas"
        finally:
            log.append("berkas ditutup")
    ```

    1. Log: `["berkas dibuka", "berkas ditutup"]`.
    2. Tanpa `try` / `finally`: log hanya `["buka"]` (pembersihan terlewat), sedangkan status response tetap `400`. Dengan `finally`: log `["buka", "tutup"]`.
    3. `POST /simpan/3`: `200`, log `koneksi dibuka`, `transaksi mulai`, `endpoint jalan (3)`, `commit`, `transaksi selesai`, `koneksi ditutup`. `POST /simpan/-1`: `500`, dengan `rollback` menggantikan `commit`.
    4. Tanpa `raise`, exception tertelan: klien menerima `500` tanpa penjelasan dan log server tidak mencatat penyebabnya (teruji: `500` dan hanya `ditelan` di log kustom, padahal endpoint melempar `400`).

## Ringkasan

- `yield` memungkinkan dependency menyiapkan sesuatu sebelum endpoint dan membersihkannya sesudahnya.
- Kode sesudah `yield` biasanya berjalan setelah response terkirim; yang di-`yield` diserahkan ke endpoint.
- Letakkan pembersihan di `finally`, supaya terjadi baik sukses maupun gagal.
- Exception dari endpoint dilemparkan kembali ke titik `yield`; tangkap dengan `except` untuk `rollback`, lalu `raise` lagi.
- Dependency berantai dibuka dari yang terdalam dan ditutup terbalik.
- Dependency `yield` bisa sudah terbuka walau validasi parameter endpoint gagal.

## Langkah berikutnya

Kembali ke daftar materi di [Modul 05: Dependency Injection](index.md). Materi berikutnya adalah [Dependency per Router](dependency-router.md). Pola `yield` ini akan dipakai untuk sesi basis data di [Modul 06](../06-basis-data/index.md).
