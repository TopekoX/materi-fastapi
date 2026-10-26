from fastapi import Depends, FastAPI

from .dependencies import wajib_pengelola
from .routers import admin, kategori, tugas

app = FastAPI(title="TugasKu API (modular)")

# Semua router dipasang di sini. Prefix "/api/v1" ditambahkan di depan prefix tiap router.
app.include_router(tugas.router, prefix="/api/v1")
app.include_router(kategori.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1", dependencies=[Depends(wajib_pengelola)])


@app.get("/", tags=["umum"])
def beranda():
    return {"pesan": "TugasKu API", "versi": "v1"}
