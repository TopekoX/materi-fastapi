from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import selectinload
from sqlmodel import Field, Relationship, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

# Basis data "produksi". Pengujian TIDAK boleh menyentuhnya.
engine = create_async_engine("sqlite+aiosqlite:///database.db")


class Kategori(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nama: str
    tugas: list["Tugas"] = Relationship(back_populates="kategori")


class TugasBuat(SQLModel):
    judul: str = Field(min_length=3, max_length=100)
    kategori_id: int | None = None


class Tugas(TugasBuat, table=True):
    id: int | None = Field(default=None, primary_key=True)
    kategori_id: int | None = Field(default=None, foreign_key="kategori.id")
    kategori: Kategori | None = Relationship(back_populates="tugas")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.siap = True  # tanda bahwa lifespan sudah berjalan
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


@app.get("/status")
async def status_aplikasi():
    return {"siap": getattr(app.state, "siap", False)}


@app.post("/tugas", status_code=status.HTTP_201_CREATED)
async def buat_tugas(data: TugasBuat, session: SessionDep):
    tugas = Tugas.model_validate(data)
    session.add(tugas)
    await session.commit()
    await session.refresh(tugas)
    return {"id": tugas.id, "judul": tugas.judul, "kategori_id": tugas.kategori_id}


@app.get("/tugas/{tugas_id}")
async def ambil_tugas(tugas_id: int, session: SessionDep):
    pernyataan = select(Tugas).where(Tugas.id == tugas_id).options(selectinload(Tugas.kategori))
    tugas = (await session.exec(pernyataan)).first()
    if tugas is None:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")
    return {"id": tugas.id, "judul": tugas.judul, "kategori": tugas.kategori.nama if tugas.kategori else None}


@app.get("/tugas")
async def daftar_tugas(session: SessionDep):
    hasil = await session.exec(select(Tugas))
    return [{"id": t.id, "judul": t.judul} for t in hasil.all()]
