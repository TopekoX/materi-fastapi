from typing import Annotated

from fastapi import Depends, FastAPI, Query

app = FastAPI()

buku = [f"Buku {n}" for n in range(1, 8)]
anggota = [f"Anggota {n}" for n in range(1, 5)]

jumlah_panggilan = 0


def parameter_halaman(
    halaman: Annotated[int, Query(ge=1)] = 1,
    batas: Annotated[int, Query(ge=1, le=50)] = 3,
):
    global jumlah_panggilan
    jumlah_panggilan += 1
    return {"awal": (halaman - 1) * batas, "batas": batas, "panggilan_ke": jumlah_panggilan}


Halaman = Annotated[dict, Depends(parameter_halaman)]


@app.get("/buku")
def daftar_buku(hal: Halaman):
    awal, batas = hal["awal"], hal["batas"]
    return {"data": buku[awal : awal + batas], "panggilan_ke": hal["panggilan_ke"]}


@app.get("/anggota")
def daftar_anggota(hal: Halaman):
    awal, batas = hal["awal"], hal["batas"]
    return {"data": anggota[awal : awal + batas], "panggilan_ke": hal["panggilan_ke"]}
