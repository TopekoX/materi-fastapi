from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query

app = FastAPI()

buku_db = {
    1: {"judul": "Dasar Python", "tersedia": True},
    2: {"judul": "Belajar FastAPI", "tersedia": False},
}

IdBuku = Annotated[int, Path(ge=1)]


def ambil_buku(buku_id: int) -> dict:
    if buku_id not in buku_db:
        raise HTTPException(
            status_code=404,
            detail=f"Buku dengan id {buku_id} tidak ditemukan",
            headers={"X-Kesalahan": "buku-tidak-ada"},
        )
    return buku_db[buku_id]


@app.get("/buku/{buku_id}")
def lihat_buku(buku_id: IdBuku):
    return ambil_buku(buku_id)


@app.post("/buku/{buku_id}/pinjam")
def pinjam_buku(buku_id: IdBuku, hari: Annotated[int, Query(ge=1)] = 7):
    buku = ambil_buku(buku_id)
    if hari > 14:
        raise HTTPException(status_code=400, detail="Lama peminjaman maksimal 14 hari")
    if not buku["tersedia"]:
        raise HTTPException(
            status_code=409,
            detail={"kode": "BUKU_DIPINJAM", "pesan": "Buku sedang dipinjam"},
        )
    buku["tersedia"] = False
    return {"judul": buku["judul"], "lama_hari": hari}
