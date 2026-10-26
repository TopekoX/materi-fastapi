from typing import Annotated

from fastapi import Depends, FastAPI

from config import Settings, get_settings

settings = get_settings()

# Dokumentasi interaktif dimatikan di produksi (sebuah pilihan; periksa kebutuhanmu)
app = FastAPI(
    title="TugasKu",
    debug=settings.mode_debug,
    docs_url=None if settings.lingkungan == "produksi" else "/docs",
    redoc_url=None,
    openapi_url=None if settings.lingkungan == "produksi" else "/openapi.json",
)


@app.get("/info")
def info(settings: Annotated[Settings, Depends(get_settings)]):
    # Hanya nilai yang aman. JANGAN mengembalikan secret_key.
    return {
        "lingkungan": settings.lingkungan,
        "mode_debug": settings.mode_debug,
        "origin_diizinkan": settings.origin_diizinkan,
        "panjang_secret_key": len(settings.secret_key.get_secret_value()),
    }
