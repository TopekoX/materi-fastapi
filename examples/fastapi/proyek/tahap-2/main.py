from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(title="TugasKu API", description="Proyek praktik tahap 2: validasi dan error terstruktur")


# --- Model ---------------------------------------------------------------
class TugasInput(BaseModel):
    judul: str = Field(min_length=3, max_length=100)
    catatan: str | None = Field(default=None, max_length=500)
    prioritas: int = Field(default=2, ge=1, le=3, description="1 = tinggi, 3 = rendah")
    selesai: bool = False


class TugasUbah(BaseModel):
    judul: str | None = Field(default=None, min_length=3, max_length=100)
    catatan: str | None = Field(default=None, max_length=500)
    prioritas: int | None = Field(default=None, ge=1, le=3)
    selesai: bool | None = None


class Tugas(TugasInput):
    id: int


# --- Penanganan error ----------------------------------------------------
class TugasTidakDitemukan(Exception):
    def __init__(self, tugas_id: int):
        self.tugas_id = tugas_id


class JudulSudahAda(Exception):
    def __init__(self, judul: str):
        self.judul = judul


def respons_galat(status_code: int, kode: str, pesan: str, rincian: list | None = None):
    isi = {"galat": {"kode": kode, "pesan": pesan, "rincian": rincian or []}}
    return JSONResponse(status_code=status_code, content=isi)


@app.exception_handler(TugasTidakDitemukan)
async def tugas_tidak_ditemukan_handler(request: Request, exc: TugasTidakDitemukan):
    return respons_galat(
        status.HTTP_404_NOT_FOUND, "TUGAS_TIDAK_ADA", f"Tugas dengan id {exc.tugas_id} tidak ditemukan"
    )


@app.exception_handler(JudulSudahAda)
async def judul_sudah_ada_handler(request: Request, exc: JudulSudahAda):
    return respons_galat(status.HTTP_409_CONFLICT, "JUDUL_SUDAH_ADA", f"Judul '{exc.judul}' sudah dipakai")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return respons_galat(exc.status_code, f"HTTP_{exc.status_code}", str(exc.detail))


@app.exception_handler(RequestValidationError)
async def validasi_handler(request: Request, exc: RequestValidationError):
    rincian = [
        {"field": ".".join(str(b) for b in galat["loc"]), "jenis": galat["type"], "pesan": galat["msg"]}
        for galat in exc.errors()
    ]
    return respons_galat(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "VALIDASI_GAGAL", "Data yang dikirim tidak valid", rincian
    )


@app.exception_handler(Exception)
async def galat_tak_terduga_handler(request: Request, exc: Exception):
    return respons_galat(status.HTTP_500_INTERNAL_SERVER_ERROR, "GALAT_SERVER", "Terjadi kesalahan pada server")


# --- Penyimpanan dalam memori ---------------------------------------------
tugas_db: dict[int, Tugas] = {}
id_berikutnya = 1

IdTugas = Annotated[int, Path(ge=1, title="ID tugas")]


def cari_tugas(tugas_id: int) -> Tugas:
    if tugas_id not in tugas_db:
        raise TugasTidakDitemukan(tugas_id)
    return tugas_db[tugas_id]


def pastikan_judul_unik(judul: str, abaikan_id: int | None = None) -> None:
    for tugas in tugas_db.values():
        if tugas.id != abaikan_id and tugas.judul.lower() == judul.lower():
            raise JudulSudahAda(judul)


# --- Endpoint ------------------------------------------------------------
@app.post("/tugas", response_model=Tugas, status_code=status.HTTP_201_CREATED)
def buat_tugas(data: TugasInput):
    global id_berikutnya
    pastikan_judul_unik(data.judul)
    tugas = Tugas(id=id_berikutnya, **data.model_dump())
    tugas_db[tugas.id] = tugas
    id_berikutnya += 1
    return tugas


@app.get("/tugas", response_model=list[Tugas])
def daftar_tugas(
    selesai: bool | None = None,
    cari: Annotated[str | None, Query(min_length=2, max_length=50)] = None,
    halaman: Annotated[int, Query(ge=1)] = 1,
    batas: Annotated[int, Query(ge=1, le=50)] = 10,
):
    hasil = list(tugas_db.values())
    if selesai is not None:
        hasil = [t for t in hasil if t.selesai == selesai]
    if cari is not None:
        hasil = [t for t in hasil if cari.lower() in t.judul.lower()]
    awal = (halaman - 1) * batas
    return hasil[awal : awal + batas]


@app.get("/tugas/{tugas_id}", response_model=Tugas)
def ambil_tugas(tugas_id: IdTugas):
    return cari_tugas(tugas_id)


@app.put("/tugas/{tugas_id}", response_model=Tugas)
def ganti_tugas(tugas_id: IdTugas, data: TugasInput):
    cari_tugas(tugas_id)
    pastikan_judul_unik(data.judul, abaikan_id=tugas_id)
    tugas = Tugas(id=tugas_id, **data.model_dump())
    tugas_db[tugas_id] = tugas
    return tugas


@app.patch("/tugas/{tugas_id}", response_model=Tugas)
def ubah_tugas(tugas_id: IdTugas, data: TugasUbah):
    tugas = cari_tugas(tugas_id)
    perubahan = data.model_dump(exclude_unset=True)
    for nama in ("judul", "prioritas", "selesai"):
        if nama in perubahan and perubahan[nama] is None:
            raise HTTPException(status_code=400, detail=f"Field '{nama}' tidak boleh null")
    if "judul" in perubahan:
        pastikan_judul_unik(perubahan["judul"], abaikan_id=tugas_id)
    tugas_baru = tugas.model_copy(update=perubahan)
    tugas_db[tugas_id] = tugas_baru
    return tugas_baru


@app.delete("/tugas/{tugas_id}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_tugas(tugas_id: IdTugas):
    cari_tugas(tugas_id)
    del tugas_db[tugas_id]
