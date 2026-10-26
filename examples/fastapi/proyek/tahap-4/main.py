import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, Path, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlmodel import Session, col, create_engine, select
from starlette.exceptions import HTTPException as StarletteHTTPException

from models import (
    Kategori,
    KategoriBuat,
    KategoriPublik,
    Pengguna,
    PenggunaBuat,
    PenggunaPublik,
    Token,
    Tugas,
    TugasBuat,
    TugasDenganKategori,
    TugasPublik,
    TugasUbah,
)

# --- Konfigurasi ---------------------------------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "Variabel environment SECRET_KEY belum diisi. "
        'Buat kunci dengan: python -c "import secrets; print(secrets.token_hex(32))"'
    )

ALGORITMA = "HS256"
MENIT_KEDALUWARSA = 30
ORIGIN_DIIZINKAN = ["http://localhost:3000"]

engine = create_engine("sqlite:///database.db", connect_args={"check_same_thread": False})
password_hash = PasswordHash.recommended()
HASH_TIRUAN = password_hash.hash("kata-sandi-tiruan")
skema_oauth2 = OAuth2PasswordBearer(tokenUrl="token")

# Tabel dikelola Alembic: jalankan `alembic upgrade head` sebelum memulai server.
app = FastAPI(title="TugasKu API", description="Proyek praktik tahap 4: autentikasi dan otorisasi")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGIN_DIIZINKAN,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# --- Penanganan error (dari tahap 2 dan 3) -----------------------------------
class TugasTidakDitemukan(Exception):
    def __init__(self, tugas_id: int):
        self.tugas_id = tugas_id


class KategoriTidakDitemukan(Exception):
    def __init__(self, kategori_id: int):
        self.kategori_id = kategori_id


class JudulSudahAda(Exception):
    def __init__(self, judul: str):
        self.judul = judul


class NamaPenggunaSudahAda(Exception):
    def __init__(self, nama: str):
        self.nama = nama


def respons_galat(status_code: int, kode: str, pesan: str, rincian: list | None = None, headers: dict | None = None):
    isi = {"galat": {"kode": kode, "pesan": pesan, "rincian": rincian or []}}
    return JSONResponse(status_code=status_code, content=isi, headers=headers)


@app.exception_handler(TugasTidakDitemukan)
async def tugas_tidak_ditemukan_handler(request: Request, exc: TugasTidakDitemukan):
    return respons_galat(404, "TUGAS_TIDAK_ADA", f"Tugas dengan id {exc.tugas_id} tidak ditemukan")


@app.exception_handler(KategoriTidakDitemukan)
async def kategori_tidak_ditemukan_handler(request: Request, exc: KategoriTidakDitemukan):
    return respons_galat(404, "KATEGORI_TIDAK_ADA", f"Kategori dengan id {exc.kategori_id} tidak ditemukan")


@app.exception_handler(JudulSudahAda)
async def judul_sudah_ada_handler(request: Request, exc: JudulSudahAda):
    return respons_galat(409, "JUDUL_SUDAH_ADA", f"Judul '{exc.judul}' sudah dipakai")


@app.exception_handler(NamaPenggunaSudahAda)
async def nama_pengguna_sudah_ada_handler(request: Request, exc: NamaPenggunaSudahAda):
    return respons_galat(409, "NAMA_PENGGUNA_SUDAH_ADA", f"Nama pengguna '{exc.nama}' sudah dipakai")


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return respons_galat(
        exc.status_code, f"HTTP_{exc.status_code}", str(exc.detail), headers=getattr(exc, "headers", None)
    )


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


# --- Session ------------------------------------------------------------------
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
IdTugas = Annotated[int, Path(ge=1, title="ID tugas")]


# --- Autentikasi -----------------------------------------------------------------
def buat_token(nama_pengguna: str) -> str:
    isi = {"sub": nama_pengguna, "exp": datetime.now(timezone.utc) + timedelta(minutes=MENIT_KEDALUWARSA)}
    return jwt.encode(isi, SECRET_KEY, algorithm=ALGORITMA)


def pengguna_saat_ini(token: Annotated[str, Depends(skema_oauth2)], session: SessionDep) -> Pengguna:
    gagal = HTTPException(
        status_code=401,
        detail="Token tidak valid atau sudah kedaluwarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        isi = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMA])
    except InvalidTokenError:
        raise gagal
    nama = isi.get("sub")
    if not nama:
        raise gagal
    pengguna = session.exec(select(Pengguna).where(Pengguna.nama_pengguna == nama)).first()
    if pengguna is None:
        raise gagal
    return pengguna


PenggunaLogin = Annotated[Pengguna, Depends(pengguna_saat_ini)]


def wajib_pengelola(pengguna: PenggunaLogin) -> Pengguna:
    if pengguna.peran != "pengelola":
        raise HTTPException(status_code=403, detail="Hanya untuk pengelola")
    return pengguna


Pengelola = Annotated[Pengguna, Depends(wajib_pengelola)]


@app.post("/daftar", response_model=PenggunaPublik, status_code=status.HTTP_201_CREATED)
def daftar(data: PenggunaBuat, session: SessionDep):
    ada = session.exec(select(Pengguna).where(Pengguna.nama_pengguna == data.nama_pengguna)).first()
    if ada is not None:
        raise NamaPenggunaSudahAda(data.nama_pengguna)
    pengguna = Pengguna(
        nama_pengguna=data.nama_pengguna,
        hash_kata_sandi=password_hash.hash(data.kata_sandi),
        peran="anggota",
    )
    session.add(pengguna)
    session.commit()
    session.refresh(pengguna)
    return pengguna


@app.post("/token", response_model=Token)
def masuk(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    pengguna = session.exec(select(Pengguna).where(Pengguna.nama_pengguna == form.username)).first()
    if pengguna is None:
        password_hash.verify(form.password, HASH_TIRUAN)  # samakan waktu respons
        sah = False
    else:
        sah = password_hash.verify(form.password, pengguna.hash_kata_sandi)
    if not sah:
        raise HTTPException(
            status_code=401,
            detail="Nama pengguna atau kata sandi salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=buat_token(pengguna.nama_pengguna), token_type="bearer")


@app.get("/saya", response_model=PenggunaPublik)
def profil_saya(pengguna: PenggunaLogin):
    return pengguna


# --- Fungsi pembantu data -------------------------------------------------------------
def pastikan_kategori_ada(session: Session, kategori_id: int | None) -> None:
    if kategori_id is not None and session.get(Kategori, kategori_id) is None:
        raise KategoriTidakDitemukan(kategori_id)


def pastikan_judul_unik(session: Session, pemilik_id: int | None, judul: str, abaikan_id: int | None = None) -> None:
    """Judul harus unik per pemilik, tanpa membedakan huruf besar-kecil."""
    pernyataan = select(Tugas).where(Tugas.pemilik_id == pemilik_id, col(Tugas.judul).ilike(judul))
    for tugas in session.exec(pernyataan).all():
        if tugas.id != abaikan_id:
            raise JudulSudahAda(judul)


def tugas_yang_boleh_diakses(tugas_id: IdTugas, pengguna: PenggunaLogin, session: SessionDep) -> Tugas:
    tugas = session.get(Tugas, tugas_id)
    if tugas is None:
        raise TugasTidakDitemukan(tugas_id)
    if tugas.pemilik_id != pengguna.id and pengguna.peran != "pengelola":
        raise HTTPException(status_code=403, detail="Tugas ini bukan milikmu")
    return tugas


TugasDiakses = Annotated[Tugas, Depends(tugas_yang_boleh_diakses)]


# --- Kategori ----------------------------------------------------------------------
@app.post("/kategori", response_model=KategoriPublik, status_code=status.HTTP_201_CREATED)
def buat_kategori(data: KategoriBuat, pengelola: Pengelola, session: SessionDep):
    kategori = Kategori.model_validate(data)
    session.add(kategori)
    session.commit()
    session.refresh(kategori)
    return kategori


@app.get("/kategori", response_model=list[KategoriPublik])
def daftar_kategori(pengguna: PenggunaLogin, session: SessionDep):
    return session.exec(select(Kategori)).all()


# --- Tugas -----------------------------------------------------------------------------
@app.post("/tugas", response_model=TugasPublik, status_code=status.HTTP_201_CREATED)
def buat_tugas(data: TugasBuat, pengguna: PenggunaLogin, session: SessionDep):
    pastikan_kategori_ada(session, data.kategori_id)
    pastikan_judul_unik(session, pengguna.id, data.judul)
    tugas = Tugas.model_validate(data, update={"pemilik_id": pengguna.id})
    session.add(tugas)
    session.commit()
    session.refresh(tugas)
    return tugas


@app.get("/tugas", response_model=list[TugasPublik])
def daftar_tugas(
    pengguna: PenggunaLogin,
    session: SessionDep,
    selesai: bool | None = None,
    kategori_id: int | None = None,
    cari: Annotated[str | None, Query(min_length=2, max_length=50)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    pernyataan = select(Tugas)
    if pengguna.peran != "pengelola":
        pernyataan = pernyataan.where(Tugas.pemilik_id == pengguna.id)
    if selesai is not None:
        pernyataan = pernyataan.where(Tugas.selesai == selesai)
    if kategori_id is not None:
        pernyataan = pernyataan.where(Tugas.kategori_id == kategori_id)
    if cari is not None:
        pernyataan = pernyataan.where(col(Tugas.judul).contains(cari))
    return session.exec(pernyataan.offset(offset).limit(limit)).all()


@app.get("/tugas/{tugas_id}", response_model=TugasDenganKategori)
def ambil_tugas(tugas: TugasDiakses):
    return tugas


@app.put("/tugas/{tugas_id}", response_model=TugasPublik)
def ganti_tugas(data: TugasBuat, tugas: TugasDiakses, session: SessionDep):
    pastikan_kategori_ada(session, data.kategori_id)
    pastikan_judul_unik(session, tugas.pemilik_id, data.judul, abaikan_id=tugas.id)
    tugas.sqlmodel_update(data.model_dump())
    session.add(tugas)
    session.commit()
    session.refresh(tugas)
    return tugas


@app.patch("/tugas/{tugas_id}", response_model=TugasPublik)
def ubah_tugas(data: TugasUbah, tugas: TugasDiakses, session: SessionDep):
    perubahan = data.model_dump(exclude_unset=True)
    for nama in ("judul", "prioritas", "selesai"):
        if nama in perubahan and perubahan[nama] is None:
            raise HTTPException(status_code=400, detail=f"Field '{nama}' tidak boleh null")
    if "judul" in perubahan:
        pastikan_judul_unik(session, tugas.pemilik_id, perubahan["judul"], abaikan_id=tugas.id)
    if "kategori_id" in perubahan:
        pastikan_kategori_ada(session, perubahan["kategori_id"])
    tugas.sqlmodel_update(perubahan)
    session.add(tugas)
    session.commit()
    session.refresh(tugas)
    return tugas


@app.delete("/tugas/{tugas_id}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_tugas(tugas: TugasDiakses, session: SessionDep):
    session.delete(tugas)
    session.commit()
