from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import Settings


@lru_cache
def get_settings() -> Settings:
    """Settings dibuat sekali, lalu dipakai ulang (berkas .env tidak dibaca di setiap request)."""
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]

# Settings dipakai juga saat aplikasi disusun (bukan hanya di endpoint)
settings = get_settings()

app = FastAPI(title=settings.nama_aplikasi, debug=settings.mode_debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origin_diizinkan,
    allow_methods=["GET"],
    allow_headers=["Authorization"],
)


@app.get("/info")
def info(settings: SettingsDep):
    # Hanya kirim nilai yang aman. JANGAN pernah mengembalikan secret_key.
    return {
        "nama_aplikasi": settings.nama_aplikasi,
        "mode_debug": settings.mode_debug,
        "database_url": settings.database_url,
        "detik_akses": settings.detik_akses,
        "origin_diizinkan": settings.origin_diizinkan,
        "panjang_secret_key": len(settings.secret_key.get_secret_value()),
    }
