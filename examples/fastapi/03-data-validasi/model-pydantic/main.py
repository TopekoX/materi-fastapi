from fastapi import FastAPI

from models import Pengguna

app = FastAPI()


@app.post("/pengguna", status_code=201)
def daftar_pengguna(pengguna: Pengguna):
    kota = pengguna.alamat.kota if pengguna.alamat else None
    return {"nama": pengguna.nama, "umur": pengguna.umur, "kota": kota, "data": pengguna.model_dump()}


@app.post("/pengguna/banyak")
def daftar_banyak(daftar: list[Pengguna]):
    return {"jumlah": len(daftar), "nama": [p.nama for p in daftar]}
