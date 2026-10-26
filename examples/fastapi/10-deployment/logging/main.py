import logging
import os
import time
import uuid

from fastapi import FastAPI, HTTPException, Request

from pengaturan_log import atur_logging, request_id_var

atur_logging(
    level=os.environ.get("TUGASKU_LOG_LEVEL", "INFO"),
    format_log=os.environ.get("TUGASKU_LOG_FORMAT", "teks"),
)

# Satu logger per modul, dinamai dengan titik sebagai hierarki: "tugasku.<bagian>"
log = logging.getLogger("tugasku.aplikasi")

app = FastAPI()


@app.middleware("http")
async def catat_request(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:8]
    token = request_id_var.set(request_id)  # semua log selama request ini membawa pengenalnya
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
        request_id_var.reset(token)  # kembalikan nilai semula setelah request selesai


@app.get("/kerja")
def kerja():
    log.debug("mulai bekerja (tingkat DEBUG)")
    log.info("pekerjaan sedang berjalan")
    log.warning("sumber daya hampir penuh")
    return {"selesai": True}


@app.get("/gagal-tak-terduga")
def gagal_tak_terduga():
    return 1 / 0


@app.get("/gagal-tertangani")
def gagal_tertangani():
    try:
        return 1 / 0
    except ZeroDivisionError:
        log.exception("pembagian dengan nol")  # mencatat pesan DAN jejak stack
        raise HTTPException(status_code=400, detail="Perhitungan tidak valid")


@app.post("/masuk")
def masuk(nama_pengguna: str, kata_sandi: str):
    # SALAH di aplikasi nyata: kata sandi dicetak ke log. Di sini hanya untuk memperlihatkan filter rahasia.
    log.info("percobaan masuk nama_pengguna=%s kata_sandi=%s", nama_pengguna, kata_sandi)
    return {"pesan": "diterima"}
