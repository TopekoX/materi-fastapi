from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI()

TOKEN_RAHASIA = "token-contoh-untuk-uji"  # hanya contoh; bukan cara autentikasi yang aman

# Penyimpanan sementara di memori
tugas_db: dict[int, dict] = {}


class TugasBaru(BaseModel):
    judul: str = Field(min_length=3, max_length=100)
    selesai: bool = False


class Tugas(TugasBaru):
    id: int


@app.get("/")
def beranda():
    return {"pesan": "TugasKu API"}


@app.post("/tugas", response_model=Tugas, status_code=status.HTTP_201_CREATED)
def buat_tugas(data: TugasBaru):
    nomor = max(tugas_db, default=0) + 1
    tugas = {"id": nomor, **data.model_dump()}
    tugas_db[nomor] = tugas
    return tugas


@app.get("/tugas", response_model=list[Tugas])
def daftar_tugas(selesai: bool | None = None):
    hasil = list(tugas_db.values())
    if selesai is not None:
        hasil = [t for t in hasil if t["selesai"] == selesai]
    return hasil


@app.get("/tugas/{tugas_id}", response_model=Tugas)
def ambil_tugas(tugas_id: int):
    if tugas_id not in tugas_db:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")
    return tugas_db[tugas_id]


@app.delete("/tugas/{tugas_id}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_tugas(tugas_id: int, x_token: Annotated[str, Header()]):
    if x_token != TOKEN_RAHASIA:
        raise HTTPException(status_code=401, detail="Token salah")
    if tugas_id not in tugas_db:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")
    del tugas_db[tugas_id]


def simpan_ringkasan(folder, tugas: list[dict]) -> str:
    """Menulis ringkasan tugas ke berkas teks di folder yang diberikan. Mengembalikan jalur berkas."""
    jalur = folder / "ringkasan.txt"
    jalur.write_text("\n".join(t["judul"] for t in tugas), encoding="utf-8")
    return str(jalur)
