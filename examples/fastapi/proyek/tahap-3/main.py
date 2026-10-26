from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlmodel import Session, col, create_engine, select
from starlette.exceptions import HTTPException as StarletteHTTPException

from models import (
    Kategori,
    KategoriBuat,
    KategoriPublik,
    Tugas,
    TugasBuat,
    TugasDenganKategori,
    TugasPublik,
    TugasUbah,
)

engine = create_engine("sqlite:///database.db", connect_args={"check_same_thread": False})

# Tabel dibuat dan diubah oleh Alembic: jalankan `alembic upgrade head` sebelum memulai server.

app = FastAPI(title="TugasKu API", description="Proyek praktik tahap 3: penyimpanan di basis data")


# --- Penanganan error (dari tahap 2) --------------------------------------
class TugasTidakDitemukan(Exception):
    def __init__(self, tugas_id: int):
        self.tugas_id = tugas_id


class KategoriTidakDitemukan(Exception):
    def __init__(self, kategori_id: int):
        self.kategori_id = kategori_id


class JudulSudahAda(Exception):
    def __init__(self, judul: str):
        self.judul = judul


def respons_galat(status_code: int, kode: str, pesan: str, rincian: list | None = None):
    isi = {"galat": {"kode": kode, "pesan": pesan, "rincian": rincian or []}}
    return JSONResponse(status_code=status_code, content=isi)


@app.exception_handler(TugasTidakDitemukan)
async def tugas_tidak_ditemukan_handler(request: Request, exc: TugasTidakDitemukan):
    return respons_galat(404, "TUGAS_TIDAK_ADA", f"Tugas dengan id {exc.tugas_id} tidak ditemukan")


@app.exception_handler(KategoriTidakDitemukan)
async def kategori_tidak_ditemukan_handler(request: Request, exc: KategoriTidakDitemukan):
    return respons_galat(404, "KATEGORI_TIDAK_ADA", f"Kategori dengan id {exc.kategori_id} tidak ditemukan")


@app.exception_handler(JudulSudahAda)
async def judul_sudah_ada_handler(request: Request, exc: JudulSudahAda):
    return respons_galat(409, "JUDUL_SUDAH_ADA", f"Judul '{exc.judul}' sudah dipakai")


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
    return respons_galat(500, "GALAT_SERVER", "Terjadi kesalahan pada server")


# --- Session dan fungsi pembantu --------------------------------------------
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
IdTugas = Annotated[int, Path(ge=1, title="ID tugas")]


def cari_tugas(session: Session, tugas_id: int) -> Tugas:
    tugas = session.get(Tugas, tugas_id)
    if tugas is None:
        raise TugasTidakDitemukan(tugas_id)
    return tugas


def pastikan_kategori_ada(session: Session, kategori_id: int | None) -> None:
    if kategori_id is not None and session.get(Kategori, kategori_id) is None:
        raise KategoriTidakDitemukan(kategori_id)


def pastikan_judul_unik(session: Session, judul: str, abaikan_id: int | None = None) -> None:
    pernyataan = select(Tugas).where(col(Tugas.judul).ilike(judul))
    for tugas in session.exec(pernyataan).all():
        if tugas.id != abaikan_id:
            raise JudulSudahAda(judul)


# --- Kategori -------------------------------------------------------------
@app.post("/kategori", response_model=KategoriPublik, status_code=status.HTTP_201_CREATED)
def buat_kategori(data: KategoriBuat, session: SessionDep):
    kategori = Kategori.model_validate(data)
    session.add(kategori)
    session.commit()
    session.refresh(kategori)
    return kategori


@app.get("/kategori", response_model=list[KategoriPublik])
def daftar_kategori(session: SessionDep):
    return session.exec(select(Kategori)).all()


# --- Tugas ----------------------------------------------------------------
@app.post("/tugas", response_model=TugasPublik, status_code=status.HTTP_201_CREATED)
def buat_tugas(data: TugasBuat, session: SessionDep):
    pastikan_kategori_ada(session, data.kategori_id)
    pastikan_judul_unik(session, data.judul)
    tugas = Tugas.model_validate(data)
    session.add(tugas)
    session.commit()
    session.refresh(tugas)
    return tugas


@app.get("/tugas", response_model=list[TugasPublik])
def daftar_tugas(
    session: SessionDep,
    selesai: bool | None = None,
    kategori_id: int | None = None,
    cari: Annotated[str | None, Query(min_length=2, max_length=50)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    pernyataan = select(Tugas)
    if selesai is not None:
        pernyataan = pernyataan.where(Tugas.selesai == selesai)
    if kategori_id is not None:
        pernyataan = pernyataan.where(Tugas.kategori_id == kategori_id)
    if cari is not None:
        pernyataan = pernyataan.where(col(Tugas.judul).contains(cari))
    return session.exec(pernyataan.offset(offset).limit(limit)).all()


@app.get("/tugas/{tugas_id}", response_model=TugasDenganKategori)
def ambil_tugas(tugas_id: IdTugas, session: SessionDep):
    return cari_tugas(session, tugas_id)


@app.put("/tugas/{tugas_id}", response_model=TugasPublik)
def ganti_tugas(tugas_id: IdTugas, data: TugasBuat, session: SessionDep):
    tugas = cari_tugas(session, tugas_id)
    pastikan_kategori_ada(session, data.kategori_id)
    pastikan_judul_unik(session, data.judul, abaikan_id=tugas_id)
    tugas.sqlmodel_update(data.model_dump())
    session.add(tugas)
    session.commit()
    session.refresh(tugas)
    return tugas


@app.patch("/tugas/{tugas_id}", response_model=TugasPublik)
def ubah_tugas(tugas_id: IdTugas, data: TugasUbah, session: SessionDep):
    tugas = cari_tugas(session, tugas_id)
    perubahan = data.model_dump(exclude_unset=True)
    for nama in ("judul", "prioritas", "selesai"):
        if nama in perubahan and perubahan[nama] is None:
            raise HTTPException(status_code=400, detail=f"Field '{nama}' tidak boleh null")
    if "judul" in perubahan:
        pastikan_judul_unik(session, perubahan["judul"], abaikan_id=tugas_id)
    if "kategori_id" in perubahan:
        pastikan_kategori_ada(session, perubahan["kategori_id"])
    tugas.sqlmodel_update(perubahan)
    session.add(tugas)
    session.commit()
    session.refresh(tugas)
    return tugas


@app.delete("/tugas/{tugas_id}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_tugas(tugas_id: IdTugas, session: SessionDep):
    tugas = cari_tugas(session, tugas_id)
    session.delete(tugas)
    session.commit()
