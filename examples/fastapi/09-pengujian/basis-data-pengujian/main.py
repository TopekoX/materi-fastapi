from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Basis data "produksi". Pengujian TIDAK boleh menyentuhnya.
engine = create_engine("sqlite:///database.db", connect_args={"check_same_thread": False})


class TugasBuat(SQLModel):
    # Skema input: aturan validasi ada di sini, karena model tabel tidak memvalidasi body
    judul: str = Field(min_length=3, max_length=100)
    selesai: bool = False


class Tugas(TugasBuat, table=True):
    id: int | None = Field(default=None, primary_key=True)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()


@app.post("/tugas", response_model=Tugas, status_code=status.HTTP_201_CREATED)
def buat_tugas(data: TugasBuat, session: SessionDep):
    tugas = Tugas.model_validate(data)  # id dibuat oleh basis data
    session.add(tugas)
    session.commit()
    session.refresh(tugas)
    return tugas


@app.get("/tugas", response_model=list[Tugas])
def daftar_tugas(session: SessionDep, selesai: bool | None = None):
    pernyataan = select(Tugas)
    if selesai is not None:
        pernyataan = pernyataan.where(Tugas.selesai == selesai)
    return session.exec(pernyataan).all()


@app.get("/tugas/{tugas_id}", response_model=Tugas)
def ambil_tugas(tugas_id: int, session: SessionDep):
    tugas = session.get(Tugas, tugas_id)
    if tugas is None:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")
    return tugas


@app.delete("/tugas/{tugas_id}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_tugas(tugas_id: int, session: SessionDep):
    tugas = session.get(Tugas, tugas_id)
    if tugas is None:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")
    session.delete(tugas)
    session.commit()
