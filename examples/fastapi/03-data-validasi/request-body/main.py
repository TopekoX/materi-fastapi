from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class TugasBaru(BaseModel):
    judul: str
    selesai: bool = False
    catatan: str | None = None


@app.post("/tugas", status_code=201)
def buat_tugas(tugas: TugasBaru):
    return {"pesan": "Tugas diterima", "data": tugas.model_dump()}


@app.put("/tugas/{tugas_id}")
def ganti_tugas(tugas_id: int, tugas: TugasBaru, simpan: bool = False):
    return {"tugas_id": tugas_id, "simpan": simpan, "data": tugas.model_dump()}
