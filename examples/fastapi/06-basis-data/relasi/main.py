from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select

engine = create_engine("sqlite:///database.db", connect_args={"check_same_thread": False})


# --- Kategori (sisi "satu") ---------------------------------------------
class KategoriDasar(SQLModel):
    nama: str = Field(min_length=2, max_length=50)


class Kategori(KategoriDasar, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tugas: list["Tugas"] = Relationship(back_populates="kategori")


# --- Tugas (sisi "banyak") ----------------------------------------------
class TugasDasar(SQLModel):
    judul: str = Field(min_length=3, max_length=100)
    selesai: bool = False
    kategori_id: int | None = Field(default=None, foreign_key="kategori.id")


class Tugas(TugasDasar, table=True):
    id: int | None = Field(default=None, primary_key=True)
    kategori: Kategori | None = Relationship(back_populates="tugas")


# --- Skema --------------------------------------------------------------
class KategoriBuat(KategoriDasar):
    pass


class KategoriPublik(KategoriDasar):
    id: int


class TugasBuat(TugasDasar):
    pass


class TugasPublik(TugasDasar):
    id: int


class TugasDenganKategori(TugasPublik):
    kategori: KategoriPublik | None = None


class KategoriDenganTugas(KategoriPublik):
    tugas: list[TugasPublik] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@app.post("/kategori", response_model=KategoriPublik, status_code=201)
def buat_kategori(data: KategoriBuat, session: SessionDep):
    kategori = Kategori.model_validate(data)
    session.add(kategori)
    session.commit()
    session.refresh(kategori)
    return kategori


@app.get("/kategori/{kategori_id}", response_model=KategoriDenganTugas)
def ambil_kategori(kategori_id: int, session: SessionDep):
    kategori = session.get(Kategori, kategori_id)
    if kategori is None:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")
    return kategori


@app.post("/tugas", response_model=TugasPublik, status_code=201)
def buat_tugas(data: TugasBuat, session: SessionDep):
    if data.kategori_id is not None and session.get(Kategori, data.kategori_id) is None:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")
    tugas = Tugas.model_validate(data)
    session.add(tugas)
    session.commit()
    session.refresh(tugas)
    return tugas


@app.get("/tugas", response_model=list[TugasPublik])
def daftar_tugas(session: SessionDep, kategori_id: int | None = None):
    pernyataan = select(Tugas)
    if kategori_id is not None:
        pernyataan = pernyataan.where(Tugas.kategori_id == kategori_id)
    return session.exec(pernyataan).all()


@app.get("/tugas/{tugas_id}", response_model=TugasDenganKategori)
def ambil_tugas(tugas_id: int, session: SessionDep):
    tugas = session.get(Tugas, tugas_id)
    if tugas is None:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")
    return tugas


@app.delete("/kategori/{kategori_id}", status_code=204)
def hapus_kategori(kategori_id: int, session: SessionDep):
    kategori = session.get(Kategori, kategori_id)
    if kategori is None:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")
    if kategori.tugas:
        raise HTTPException(status_code=409, detail="Kategori masih memiliki tugas")
    session.delete(kategori)
    session.commit()
