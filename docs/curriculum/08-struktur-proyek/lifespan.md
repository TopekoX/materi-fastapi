# Lifespan: Mulai dan Berhenti

## Tujuan pembelajaran

Setelah membaca halaman ini, kamu mampu:

- [ ] Menjelaskan apa yang dimaksud peristiwa mulai (*startup*) dan berhenti (*shutdown*) aplikasi.
- [ ] Menulis `lifespan` dengan `@asynccontextmanager` dan memasangnya di `FastAPI(lifespan=...)`.
- [ ] Menyiapkan sumber daya saat mulai, membagikannya lewat `app.state`, dan membersihkannya saat berhenti.
- [ ] Menjelaskan apa yang terjadi bila persiapan gagal.
- [ ] Menguji `lifespan` dengan `TestClient` dan mengenali kapan ia tidak dijalankan.

## Prasyarat

- Sudah membaca [Background Task](background-task.md) dan [Konfigurasi dan Environment](konfigurasi-environment.md).
- Sudah membaca [Dependency dengan yield](../05-dependency-injection/dependency-yield.md). Pola sebelum dan sesudah `yield` sama.

!!! info "Versi yang diuji"
    Kode dan output di halaman ini dijalankan dengan **Python 3.14.7** dan **FastAPI 0.162.0** (dengan Starlette 1.10.0) di Windows. Daftar versi lain ada di [Versi yang dipakai di materi ini](../01-pengenalan/instalasi-dan-venv.md#versi-yang-dipakai-di-materi-ini). Versi lain dan sistem operasi lain **belum diuji**.

## Konsep

Beberapa pekerjaan sebaiknya dilakukan **sekali** saat aplikasi mulai, bukan di setiap request: membuka koneksi, memuat model atau berkas besar, atau membuat tabel. Pekerjaan pembersihan yang berpasangan, seperti menutup koneksi, sebaiknya dilakukan **sekali** saat aplikasi berhenti.

Di modul sebelumnya kamu sudah memakai pola ini tanpa membahasnya: `SQLModel.metadata.create_all(engine)` di [Koneksi ke Basis Data](../06-basis-data/koneksi-basis-data.md) dan `engine.dispose()` di [Sesi Basis Data Async](../06-basis-data/sesi-async.md). Keduanya berada di fungsi `lifespan`.

Menurut dokumentasi FastAPI, `lifespan` adalah cara yang dianjurkan; `@app.on_event("startup")` dan `"shutdown"` dinyatakan usang. Dokumentasi juga memperingatkan: bila `lifespan` diberikan, handler `on_event` tidak lagi dipanggil. Pakai salah satu, jangan dicampur.

### Cara kerjanya

`lifespan` adalah fungsi yang memakai `yield`, seperti dependency `yield`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # sebelum yield: dijalankan sekali saat MULAI
    ...
    yield
    # sesudah yield: dijalankan sekali saat BERHENTI
    ...
```

- Kode sebelum `yield` berjalan **sebelum** aplikasi menerima request pertama.
- Aplikasi melayani request selama `yield` "menunggu".
- Kode sesudah `yield` berjalan saat aplikasi berhenti.

`@asynccontextmanager` (dari `contextlib`) mengubah fungsi ini menjadi *context manager* async yang dimengerti FastAPI.

## Kode lengkap

Simpan sebagai `main.py`:

```python title="main.py"
--8<-- "fastapi/08-struktur-proyek/lifespan/main.py"
```

## Penjelasan kode

### Sumber daya tiruan

`SumberDaya` mewakili koneksi basis data atau klien HTTP: `buka()` dan `tutup()` mengubah status `terbuka` dan menulis ke `lifespan.log`. Berkas log dipakai agar kejadian tetap terlihat setelah proses berhenti.

### Fungsi `lifespan`

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    catat("startup: mulai")
    sumber_daya = SumberDaya("koneksi")
    sumber_daya.buka()
    app.state.sumber_daya = sumber_daya
    catat("startup: selesai, aplikasi siap menerima request")

    try:
        yield
    finally:
        catat("shutdown: mulai")
        sumber_daya.tutup()
        catat("shutdown: selesai")
```

- `app.state` adalah tempat menyimpan objek yang dipakai seluruh aplikasi. Endpoint membacanya lewat `request.app.state`.
- `try`/`finally` di sekitar `yield` memastikan pembersihan dijalankan sekalipun aplikasi berhenti karena error, mengikuti pola dependency `yield`.

### Memasangnya

```python
app = FastAPI(lifespan=lifespan)
```

### Memakai sumber daya di endpoint

```python
@app.get("/status")
def status(request: Request):
    sumber_daya: SumberDaya = request.app.state.sumber_daya
    return {"sumber_daya": sumber_daya.nama, "terbuka": sumber_daya.terbuka}
```

`request.app.state` mengembalikan objek yang sama yang disiapkan saat mulai.

## Menjalankan

```powershell
fastapi run main.py
```

Server berjalan di `http://127.0.0.1:8000`. Jika port 8000 dipakai aplikasi lain, tambahkan `--port 8001` dan sesuaikan URL di bawah. (`fastapi dev` juga bisa dipakai.) Berkas `lifespan.log` dibuat di folder kerja.

## Mencoba request

### Saat mulai

Dengan `curl.exe` setelah server berjalan:

```powershell
curl.exe http://127.0.0.1:8000/status
```

```json
{"sumber_daya":"koneksi","terbuka":true}
```

`GET /log`:

```json
["[20:50:25] startup: mulai","[20:50:25] koneksi: dibuka","[20:50:25] startup: selesai, aplikasi siap menerima request"]
```

Kode sebelum `yield` sudah berjalan sebelum request pertama datang. Log server mencatat `Waiting for application startup.` lalu `Application startup complete.`

### Saat berhenti

Pada pengujian, server dihentikan dengan perintah `timeout` di Windows, dan baris `shutdown` **tidak** muncul di `lifespan.log`: penghentian itu bersifat paksa, bukan penghentian baik-baik. Pada penggunaan nyata, kamu menghentikan server dengan `Ctrl+C` di terminal; perilaku itu tidak diuji di sini. Untuk membuktikan bagian `shutdown`, kita memakai `TestClient`, yang menjalankan `lifespan` secara terkendali.

### Menguji dengan `TestClient`

```python
from fastapi.testclient import TestClient
import main

# Tanpa "with": lifespan TIDAK dijalankan
c = TestClient(main.app, raise_server_exceptions=False)
print(c.get("/status").status_code)          # 500

# Dengan "with": lifespan dijalankan (mulai di awal blok, berhenti di akhir)
with TestClient(main.app) as c2:
    print(c2.get("/status").json())           # {'sumber_daya': 'koneksi', 'terbuka': True}
    print(c2.get("/gagal").status_code)       # 500
    print(c2.get("/status").json()["terbuka"])  # True
print(main.app.state.sumber_daya.terbuka)     # False
```

Hasil sebenarnya:

| Langkah | Hasil |
|---|---|
| `TestClient` tanpa `with`, `GET /status` | `500` (`app.state.sumber_daya` belum ada karena `lifespan` tidak dijalankan) |
| Di dalam `with`, `GET /status` | `{'sumber_daya': 'koneksi', 'terbuka': True}` |
| Di dalam `with`, `GET /gagal` | `500`, tetapi sumber daya tetap terbuka |
| Di dalam `with`, `GET /status` lagi | `terbuka` tetap `True` |
| Setelah keluar dari `with` | `terbuka` menjadi `False` |

Log yang dihasilkan menunjukkan urutan lengkap:

```text
startup: mulai
koneksi: dibuka
startup: selesai, aplikasi siap menerima request
shutdown: mulai
koneksi: ditutup
shutdown: selesai
```

Dua pelajaran: `lifespan` hanya berjalan bila aplikasi dijalankan lewat `with TestClient(...)` (penting untuk [Modul 09](../09-pengujian/index.md)), dan endpoint yang gagal tidak mengganggu `lifespan`.

### Bila persiapan gagal

`main_gagal_mulai.py` melempar exception sebelum `yield`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    raise RuntimeError("tidak bisa membuka koneksi basis data")
    yield
```

Menjalankan `fastapi run main_gagal_mulai.py` menghasilkan:

```text
RuntimeError: tidak bisa membuka koneksi basis data
ERROR:    Application startup failed. Exiting.
```

Server tidak mulai: pada pengujian, port tidak menjawab sama sekali. Ini perilaku yang diinginkan. Lebih baik aplikasi gagal jelas saat mulai daripada berjalan tanpa sumber daya yang dibutuhkan.

### Dokumentasi otomatis

`lifespan` tidak muncul di `/openapi.json`. Tampilan Swagger UI **belum diverifikasi** lewat browser.

## Kesalahan umum

| Kesalahan | Akibat |
|---|---|
| Memakai `@app.on_event("startup")` di kode baru | Dinyatakan usang di dokumentasi FastAPI. Pakai `lifespan`. |
| Mencampur `lifespan` dan `on_event` | Handler `on_event` tidak dipanggil bila `lifespan` diberikan (dokumentasi FastAPI). |
| `TestClient(app)` tanpa `with` | `lifespan` tidak jalan; `app.state` kosong (teruji: `500`). |
| Lupa `yield` | `lifespan` tidak valid sebagai context manager. Tidak diuji di sini. |
| Pembersihan tanpa `try`/`finally` | Pembersihan terlewat bila ada error saat berjalan. Pola sama dengan dependency `yield`. |
| Menyimpan state di variabel global | Sulit diganti di pengujian. Pakai `app.state`. |
| Pekerjaan berat dan lama di startup | Server baru menerima request setelah selesai. |
| Berharap `shutdown` tercatat saat proses dimatikan paksa | Tidak berjalan (teruji dengan `timeout` di Windows). Hentikan dengan `Ctrl+C`; tidak diuji di sini. |
| `lifespan` di sub-aplikasi | Menurut dokumentasi FastAPI, `lifespan` hanya berjalan untuk aplikasi utama. Tidak dibahas di sini. |

## Latihan

1. **Dasar.** Kapan kode sebelum `yield` dan kode sesudah `yield` dijalankan?
2. **Prediksi.** Apa isi `GET /status` bila `lifespan` tidak dijalankan? Bagaimana dengan `TestClient`?
3. **Praktik.** Tambahkan sumber daya kedua `"cache"` yang dibuka sesudah `"koneksi"` dan ditutup **sebelum** `"koneksi"` saat berhenti. Bagaimana urutan di `finally`?
4. **Analisis.** Mengapa aplikasi sebaiknya gagal mulai bila koneksi wajib tidak bisa dibuka?

??? success "Kunci jawaban"
    Jawaban 2 dan 4 mengacu pada hasil uji di atas. Jawaban 1 dan 3 adalah penalaran dari penjelasan halaman ini; jawaban 3 tidak dijalankan.

    1. Sebelum `yield`: sekali saat aplikasi mulai, sebelum request pertama. Sesudah `yield`: sekali saat aplikasi berhenti.
    2. Endpoint `GET /status` menjawab `500` karena `app.state.sumber_daya` belum ada. `TestClient` tanpa `with` menunjukkannya; dengan `with`, hasilnya `{'sumber_daya': 'koneksi', 'terbuka': True}`.
    3. Buka `koneksi`, lalu `cache`, dalam urutan itu sebelum `yield`. Di `finally`, tutup `cache` lebih dulu, lalu `koneksi` (kebalikan urutan membuka), sama seperti penutupan dependency `yield` berantai di Modul 05.
    4. Tanpa sumber daya yang wajib, aplikasi akan gagal di setiap request dengan pesan yang membingungkan. Gagal saat mulai membuat masalah segera terlihat (teruji: `Application startup failed. Exiting.`) dan mencegah aplikasi setengah siap menerima lalu lintas.

## Ringkasan

- `lifespan` menjalankan kode sekali saat aplikasi mulai (sebelum `yield`) dan sekali saat berhenti (sesudah `yield`).
- Dipasang dengan `FastAPI(lifespan=lifespan)`; `@asynccontextmanager` membungkus fungsinya.
- Bagikan sumber daya lewat `app.state`, dan bersihkan di `finally`.
- Bila persiapan gagal, aplikasi tidak mulai.
- `on_event` usang; jangan dicampur dengan `lifespan`.
- Di pengujian, `lifespan` hanya jalan bila memakai `with TestClient(app)`.

## Langkah berikutnya

Lanjut ke [Proyek: Memecah TugasKu](refaktor-tugasku.md), atau kembali ke daftar materi di [Modul 08: Struktur Proyek](index.md).
