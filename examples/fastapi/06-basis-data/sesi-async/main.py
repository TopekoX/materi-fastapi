from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import selectinload
from sqlmodel import Field, Relationship, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

# Driver async untuk SQLite: aiosqlite (sqlite+aiosqlite://)
engine = create_async_engine("sqlite+aiosqlite:///database.db")


class Kategori(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nama: str
    tugas: list["Tugas"] = Relationship(back_populates="kategori")


class Tugas(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    judul: str
    selesai: bool = False
    kategori_id: int | None = Field(default=None, foreign_key="kategori.id")
    kategori: Kategori | None = Relationship(back_populates="tugas")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create_all tidak punya versi await, jadi dijalankan lewat run_sync
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    await engine.dispose()  # menutup koneksi saat aplikasi berhenti


app = FastAPI(lifespan=lifespan)


async def get_session():
    # expire_on_commit=False: atribut tetap terbaca setelah commit tanpa query tambahan
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


@app.post("/kategori", status_code=201)
async def buat_kategori(nama: str, session: SessionDep):
    kategori = Kategori(nama=nama)
    session.add(kategori)
    await session.commit()
    await session.refresh(kategori)
    return {"id": kategori.id, "nama": kategori.nama}


@app.post("/tugas", status_code=201)
async def buat_tugas(judul: str, session: SessionDep, kategori_id: int | None = None):
    tugas = Tugas(judul=judul, kategori_id=kategori_id)
    session.add(tugas)
    await session.commit()
    await session.refresh(tugas)
    return tugas


@app.get("/tugas")
async def daftar_tugas(session: SessionDep):
    hasil = await session.exec(select(Tugas))
    return hasil.all()


# Benar: relasi dimuat bersama kueri dengan selectinload
@app.get("/tugas/{tugas_id}")
async def ambil_tugas(tugas_id: int, session: SessionDep):
    pernyataan = select(Tugas).where(Tugas.id == tugas_id).options(selectinload(Tugas.kategori))
    tugas = (await session.exec(pernyataan)).first()
    if tugas is None:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")
    return {
        "id": tugas.id,
        "judul": tugas.judul,
        "kategori": tugas.kategori.nama if tugas.kategori else None,
    }


# Salah (sengaja): membaca relasi tanpa memuatnya lebih dulu
@app.get("/tugas/{tugas_id}/salah")
async def ambil_tugas_salah(tugas_id: int, session: SessionDep):
    tugas = await session.get(Tugas, tugas_id)
    if tugas is None:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")
    return {"judul": tugas.judul, "kategori": tugas.kategori.nama if tugas.kategori else None}
