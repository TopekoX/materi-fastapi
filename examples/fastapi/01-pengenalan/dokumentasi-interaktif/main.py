from fastapi import FastAPI

app = FastAPI(
    title="Belajar FastAPI",
    description="Contoh dokumentasi interaktif otomatis.",
    version="0.1.0",
)


@app.get("/", summary="Halaman utama", tags=["Umum"])
def halaman_utama():
    """Mengembalikan pesan sambutan."""
    return {"pesan": "Halo dari dokumentasi interaktif!"}


@app.get("/kesehatan", summary="Cek kesehatan", tags=["Umum"])
def kesehatan():
    """Memeriksa bahwa aplikasi hidup."""
    return {"status": "ok"}


@app.post("/tugas", status_code=201, summary="Buat tugas", tags=["Tugas"])
def buat_tugas():
    """Membuat tugas baru. Contoh ini belum menyimpan data."""
    return {"aksi": "membuat tugas baru"}
