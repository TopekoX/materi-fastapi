from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Path, Query

app = FastAPI()

buku_db = {
    1: {"id": 1, "judul": "Dasar Python", "dipinjam": False},
    2: {"id": 2, "judul": "Belajar FastAPI", "dipinjam": True},
    3: {"id": 3, "judul": "Basis Data", "dipinjam": False},
    4: {"id": 4, "judul": "Jaringan Komputer", "dipinjam": False},
}


# 1. Dependency fungsi yang mengambil data atau menolak request
def ambil_buku(buku_id: Annotated[int, Path(ge=1)]) -> dict:
    if buku_id not in buku_db:
        raise HTTPException(status_code=404, detail=f"Buku {buku_id} tidak ditemukan")
    return buku_db[buku_id]


BukuDitemukan = Annotated[dict, Depends(ambil_buku)]


# 2. Dependency berupa class
class Paginasi:
    def __init__(
        self,
        halaman: Annotated[int, Query(ge=1)] = 1,
        batas: Annotated[int, Query(ge=1, le=50)] = 2,
    ):
        self.halaman = halaman
        self.batas = batas
        self.awal = (halaman - 1) * batas


# 3. Dependency yang hanya memeriksa (nilainya tidak dipakai endpoint)
KLIEN_DIIZINKAN = {"web", "mobile"}


def wajib_klien(x_klien: Annotated[str, Header()]) -> None:
    if x_klien not in KLIEN_DIIZINKAN:
        raise HTTPException(status_code=400, detail="Header X-Klien tidak dikenal")


@app.get("/buku")
def daftar_buku(paginasi: Annotated[Paginasi, Depends()]):
    semua = list(buku_db.values())
    hasil = semua[paginasi.awal : paginasi.awal + paginasi.batas]
    return {"halaman": paginasi.halaman, "batas": paginasi.batas, "data": hasil}


@app.get("/buku/{buku_id}")
def lihat_buku(buku: BukuDitemukan):
    return buku


@app.delete("/buku/{buku_id}", status_code=204)
def hapus_buku(buku: BukuDitemukan):
    del buku_db[buku["id"]]


@app.post("/buku/{buku_id}/pinjam", dependencies=[Depends(wajib_klien)])
def pinjam_buku(buku: BukuDitemukan):
    if buku["dipinjam"]:
        raise HTTPException(status_code=409, detail="Buku sedang dipinjam")
    buku["dipinjam"] = True
    return buku
