from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import inspect, text
from sqlmodel import Field, Session, SQLModel, create_engine, select

# 1. Alamat basis data: berkas SQLite bernama database.db di folder kerja
sqlite_url = "sqlite:///database.db"

# 2. Engine: satu untuk seluruh aplikasi, memegang koneksi ke basis data
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


# 3. Model tabel: kelas Python yang menjadi tabel
class Catatan(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    isi: str


# 4. Membuat tabel saat aplikasi mulai
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)


# 5. Dependency: satu sesi per request, ditutup otomatis (pola yield dari Modul 05)
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/db/ping")
def ping(session: SessionDep):
    hasil = session.exec(text("SELECT 1")).scalar()
    return {"hasil": hasil}


@app.get("/db/tabel")
def daftar_tabel():
    return {"tabel": inspect(engine).get_table_names()}


@app.post("/catatan", status_code=201)
def buat_catatan(catatan: Catatan, session: SessionDep):
    session.add(catatan)
    session.commit()
    session.refresh(catatan)
    return catatan


@app.get("/catatan")
def daftar_catatan(session: SessionDep):
    return session.exec(select(Catatan)).all()
