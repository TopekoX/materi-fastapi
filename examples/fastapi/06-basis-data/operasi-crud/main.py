from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, col, create_engine, select

engine = create_engine("sqlite:///database.db", connect_args={"check_same_thread": False})


class TugasDasar(SQLModel):
    judul: str = Field(min_length=3, max_length=100)
    catatan: str | None = Field(default=None, max_length=500)
    prioritas: int = Field(default=2, ge=1, le=3)
    selesai: bool = False


class Tugas(TugasDasar, table=True):
    id: int | None = Field(default=None, primary_key=True)


class TugasBuat(TugasDasar):
    pass


class TugasPublik(TugasDasar):
    id: int


class TugasUbah(SQLModel):
    judul: str | None = Field(default=None, min_length=3, max_length=100)
    catatan: str | None = Field(default=None, max_length=500)
    prioritas: int | None = Field(default=None, ge=1, le=3)
    selesai: bool | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def cari_tugas(session: Session, tugas_id: int) -> Tugas:
    tugas = session.get(Tugas, tugas_id)
    if tugas is None:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")
    return tugas


# CREATE
@app.post("/tugas", response_model=TugasPublik, status_code=201)
def buat_tugas(data: TugasBuat, session: SessionDep):
    tugas = Tugas.model_validate(data)
    session.add(tugas)
    session.commit()
    session.refresh(tugas)
    return tugas


# READ (daftar, dengan filter dan paginasi)
@app.get("/tugas", response_model=list[TugasPublik])
def daftar_tugas(
    session: SessionDep,
    selesai: bool | None = None,
    cari: Annotated[str | None, Query(min_length=2, max_length=50)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    pernyataan = select(Tugas)
    if selesai is not None:
        pernyataan = pernyataan.where(Tugas.selesai == selesai)
    if cari is not None:
        pernyataan = pernyataan.where(col(Tugas.judul).contains(cari))
    return session.exec(pernyataan.offset(offset).limit(limit)).all()


# READ (satu)
@app.get("/tugas/{tugas_id}", response_model=TugasPublik)
def ambil_tugas(tugas_id: int, session: SessionDep):
    return cari_tugas(session, tugas_id)


# UPDATE (sebagian)
@app.patch("/tugas/{tugas_id}", response_model=TugasPublik)
def ubah_tugas(tugas_id: int, data: TugasUbah, session: SessionDep):
    tugas = cari_tugas(session, tugas_id)
    perubahan = data.model_dump(exclude_unset=True)
    tugas.sqlmodel_update(perubahan)
    session.add(tugas)
    session.commit()
    session.refresh(tugas)
    return tugas


# DELETE
@app.delete("/tugas/{tugas_id}", status_code=204)
def hapus_tugas(tugas_id: int, session: SessionDep):
    tugas = cari_tugas(session, tugas_id)
    session.delete(tugas)
    session.commit()
