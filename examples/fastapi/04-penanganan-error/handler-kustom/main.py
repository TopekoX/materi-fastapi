from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()


class BukuTidakDitemukan(Exception):
    def __init__(self, buku_id: int):
        self.buku_id = buku_id


def respons_galat(status_code: int, kode: str, pesan: str, rincian: list | None = None):
    isi = {"galat": {"kode": kode, "pesan": pesan, "rincian": rincian or []}}
    return JSONResponse(status_code=status_code, content=isi)


@app.exception_handler(BukuTidakDitemukan)
async def buku_tidak_ditemukan_handler(request: Request, exc: BukuTidakDitemukan):
    return respons_galat(404, "BUKU_TIDAK_ADA", f"Buku dengan id {exc.buku_id} tidak ditemukan")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return respons_galat(exc.status_code, f"HTTP_{exc.status_code}", str(exc.detail))


@app.exception_handler(RequestValidationError)
async def validasi_handler(request: Request, exc: RequestValidationError):
    rincian = [
        {"field": ".".join(str(b) for b in galat["loc"]), "jenis": galat["type"], "pesan": galat["msg"]}
        for galat in exc.errors()
    ]
    return respons_galat(422, "VALIDASI_GAGAL", "Data yang dikirim tidak valid", rincian)


@app.exception_handler(Exception)
async def galat_tak_terduga_handler(request: Request, exc: Exception):
    return respons_galat(500, "GALAT_SERVER", "Terjadi kesalahan pada server")


class BukuBaru(BaseModel):
    judul: str = Field(min_length=3)
    tahun: int = Field(ge=1900)


buku_db = {1: {"id": 1, "judul": "Dasar Python", "tahun": 2020}}


@app.get("/buku/{buku_id}")
def lihat_buku(buku_id: int):
    if buku_id not in buku_db:
        raise BukuTidakDitemukan(buku_id)
    return buku_db[buku_id]


@app.post("/buku", status_code=201)
def tambah_buku(buku: BukuBaru):
    if any(b["judul"] == buku.judul for b in buku_db.values()):
        raise HTTPException(status_code=409, detail="Judul sudah ada")
    baru = {"id": max(buku_db) + 1, **buku.model_dump()}
    buku_db[baru["id"]] = baru
    return baru


@app.get("/rusak")
def endpoint_rusak():
    return 1 / 0
