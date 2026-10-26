from http import HTTPStatus

from fastapi import FastAPI, status

app = FastAPI()

catatan_db: dict[int, str] = {1: "Belajar status code"}


@app.get("/catatan")
def daftar_catatan():
    return catatan_db


@app.post("/catatan", status_code=status.HTTP_201_CREATED)
def buat_catatan(isi: str):
    nomor = max(catatan_db, default=0) + 1
    catatan_db[nomor] = isi
    return {"nomor": nomor, "isi": isi}


@app.delete("/catatan/{nomor}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_catatan(nomor: int):
    catatan_db.pop(nomor, None)


@app.post("/antrean", status_code=HTTPStatus.ACCEPTED)
def masuk_antrean(isi: str):
    return {"pesan": "Diterima, akan diproses nanti", "isi": isi}


@app.get("/rusak")
def endpoint_rusak():
    return 1 / 0
