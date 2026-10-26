from typing import Annotated

from fastapi import Depends, FastAPI
from sqlmodel import Session, create_engine, select

from models import Tugas

engine = create_engine("sqlite:///database.db", connect_args={"check_same_thread": False})

# Perhatikan: tidak ada SQLModel.metadata.create_all di sini.
# Tabel dibuat dan diubah oleh Alembic (alembic upgrade head).

app = FastAPI()


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@app.post("/tugas", response_model=Tugas, status_code=201)
def buat_tugas(tugas: Tugas, session: SessionDep):
    tugas.id = None
    session.add(tugas)
    session.commit()
    session.refresh(tugas)
    return tugas


@app.get("/tugas", response_model=list[Tugas])
def daftar_tugas(session: SessionDep):
    return session.exec(select(Tugas)).all()
