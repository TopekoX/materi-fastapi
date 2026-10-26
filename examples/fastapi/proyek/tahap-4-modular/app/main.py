from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .errors import pasang_penangan_error
from .routers import auth, kategori, tugas

settings = get_settings()

app = FastAPI(title=settings.nama_aplikasi, description="TugasKu API (versi modular)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origin_diizinkan,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

pasang_penangan_error(app)

app.include_router(auth.router)
app.include_router(kategori.router)
app.include_router(tugas.router)
