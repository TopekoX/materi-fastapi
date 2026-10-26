from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select

engine = create_engine("sqlite:///database.db", connect_args={"check_same_thread": False})


# Skema dasar: field yang dimiliki bersama, lengkap dengan aturan validasi
class TugasDasar(SQLModel):
    judul: str = Field(min_length=3, max_length=100)
    catatan: str | None = Field(default=None, max_length=500)
    prioritas: int = Field(default=2, ge=1, le=3)
    selesai: bool = False


# Model tabel: yang disimpan di basis data (ada id dan kolom internal)
class Tugas(TugasDasar, table=True):
    id: int | None = Field(default=None, primary_key=True)
    catatan_internal: str | None = None


# Skema input: yang boleh dikirim klien saat membuat tugas
class TugasBuat(TugasDasar):
    pass


# Skema output: yang dikembalikan ke klien (ada id, tanpa catatan_internal)
class TugasPublik(TugasDasar):
    id: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@app.post("/tugas", response_model=TugasPublik, status_code=201)
def buat_tugas(data: TugasBuat, session: SessionDep):
    tugas = Tugas.model_validate(data, update={"catatan_internal": "dibuat lewat API"})
    session.add(tugas)
    session.commit()
    session.refresh(tugas)
    return tugas


@app.get("/tugas", response_model=list[TugasPublik])
def daftar_tugas(session: SessionDep):
    return session.exec(select(Tugas)).all()


@app.get("/tugas/{tugas_id}", response_model=TugasPublik)
def ambil_tugas(tugas_id: int, session: SessionDep):
    tugas = session.get(Tugas, tugas_id)
    if tugas is None:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")
    return tugas


@app.get("/tugas/{tugas_id}/mentah")
def ambil_tugas_mentah(tugas_id: int, session: SessionDep):
    """Hanya untuk percobaan: mengembalikan model tabel apa adanya."""
    tugas = session.get(Tugas, tugas_id)
    if tugas is None:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")
    return tugas
