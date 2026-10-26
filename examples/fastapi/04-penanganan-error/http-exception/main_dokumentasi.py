from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

buku_db = {1: "Dasar Python"}


class Pesan(BaseModel):
    detail: str


@app.get(
    "/buku/{buku_id}",
    responses={404: {"model": Pesan, "description": "Buku tidak ditemukan"}},
)
def lihat_buku(buku_id: int):
    if buku_id not in buku_db:
        raise HTTPException(status_code=404, detail="Buku tidak ditemukan")
    return {"judul": buku_db[buku_id]}
