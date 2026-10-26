from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field

app = FastAPI(title="TugasKu API", description="Proyek praktik tahap 1: CRUD dalam memori")


class TugasInput(BaseModel):
    judul: str = Field(min_length=3, max_length=100)
    catatan: str | None = Field(default=None, max_length=500)
    prioritas: int = Field(default=2, ge=1, le=3, description="1 = tinggi, 3 = rendah")
    selesai: bool = False


class Tugas(TugasInput):
    id: int


# Penyimpanan dalam memori: hilang saat server dimulai ulang.
tugas_db: dict[int, Tugas] = {}
id_berikutnya = 1

IdTugas = Annotated[int, Path(ge=1, title="ID tugas")]


def cari_tugas(tugas_id: int) -> Tugas:
    if tugas_id not in tugas_db:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")
    return tugas_db[tugas_id]


@app.post("/tugas", response_model=Tugas, status_code=201)
def buat_tugas(data: TugasInput):
    global id_berikutnya
    tugas = Tugas(id=id_berikutnya, **data.model_dump())
    tugas_db[tugas.id] = tugas
    id_berikutnya += 1
    return tugas


@app.get("/tugas", response_model=list[Tugas])
def daftar_tugas(
    selesai: bool | None = None,
    cari: Annotated[str | None, Query(min_length=2, max_length=50)] = None,
    halaman: Annotated[int, Query(ge=1)] = 1,
    batas: Annotated[int, Query(ge=1, le=50)] = 10,
):
    hasil = list(tugas_db.values())
    if selesai is not None:
        hasil = [t for t in hasil if t.selesai == selesai]
    if cari is not None:
        hasil = [t for t in hasil if cari.lower() in t.judul.lower()]
    awal = (halaman - 1) * batas
    return hasil[awal : awal + batas]


@app.get("/tugas/{tugas_id}", response_model=Tugas)
def ambil_tugas(tugas_id: IdTugas):
    return cari_tugas(tugas_id)


@app.put("/tugas/{tugas_id}", response_model=Tugas)
def ganti_tugas(tugas_id: IdTugas, data: TugasInput):
    cari_tugas(tugas_id)
    tugas = Tugas(id=tugas_id, **data.model_dump())
    tugas_db[tugas_id] = tugas
    return tugas


@app.delete("/tugas/{tugas_id}", status_code=204)
def hapus_tugas(tugas_id: IdTugas):
    cari_tugas(tugas_id)
    del tugas_db[tugas_id]
