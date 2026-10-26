import logging
import time
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import text

from .config import get_settings
from .database import SessionDep
from .errors import pasang_penangan_error
from .pengaturan_log import atur_logging, request_id_var
from .routers import auth, kategori, tugas

settings = get_settings()
atur_logging(level=settings.log_level, format_log=settings.log_format)
log = logging.getLogger("tugasku.aplikasi")

# Di produksi dokumentasi interaktif ditutup (keputusan, bukan keharusan; lihat Checklist Rilis)
produksi = settings.lingkungan == "produksi"
app = FastAPI(
    title=settings.nama_aplikasi,
    description="TugasKu API (siap deploy)",
    docs_url=None if produksi else "/docs",
    redoc_url=None if produksi else "/redoc",
    openapi_url=None if produksi else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origin_diizinkan,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def catat_request(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:8]
    token = request_id_var.set(request_id)
    mulai = time.perf_counter()
    try:
        response = await call_next(request)
        durasi_ms = (time.perf_counter() - mulai) * 1000
        log.info("%s %s -> %s (%.1f ms)", request.method, request.url.path, response.status_code, durasi_ms)
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception:
        log.exception("request gagal: %s %s", request.method, request.url.path)
        raise
    finally:
        request_id_var.reset(token)


pasang_penangan_error(app)


@app.get("/kesehatan", tags=["operasional"])
def kesehatan():
    """Liveness: proses hidup dan bisa menjawab. Tidak menyentuh basis data."""
    return {"status": "ok"}


@app.get("/siap", tags=["operasional"])
def siap(session: SessionDep):
    """Readiness: aplikasi bisa bekerja, termasuk menjangkau basis data."""
    try:
        session.exec(text("SELECT 1"))
    except Exception:
        log.exception("pemeriksaan kesiapan gagal")
        raise HTTPException(status_code=503, detail="Basis data belum siap")
    return {"status": "siap"}


app.include_router(auth.router)
app.include_router(kategori.router)
app.include_router(tugas.router)
