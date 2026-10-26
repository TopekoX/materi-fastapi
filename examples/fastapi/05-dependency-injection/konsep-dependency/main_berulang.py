from typing import Annotated

from fastapi import FastAPI, Query

app = FastAPI()

buku = [f"Buku {n}" for n in range(1, 8)]
anggota = [f"Anggota {n}" for n in range(1, 5)]


@app.get("/buku")
def daftar_buku(
    halaman: Annotated[int, Query(ge=1)] = 1,
    batas: Annotated[int, Query(ge=1, le=50)] = 3,
):
    awal = (halaman - 1) * batas
    return buku[awal : awal + batas]


@app.get("/anggota")
def daftar_anggota(
    halaman: Annotated[int, Query(ge=1)] = 1,
    batas: Annotated[int, Query(ge=1, le=50)] = 3,
):
    awal = (halaman - 1) * batas
    return anggota[awal : awal + batas]
