from fastapi import FastAPI

app = FastAPI()


@app.get("/tugas")
def daftar_tugas():
    return {"aksi": "mengambil daftar tugas"}


@app.post("/tugas", status_code=201)
def buat_tugas():
    return {"aksi": "membuat tugas baru"}


@app.get("/tugas/1")
def detail_tugas():
    return {"aksi": "mengambil tugas nomor 1"}


@app.put("/tugas/1")
def ganti_tugas():
    return {"aksi": "mengganti tugas nomor 1"}


@app.delete("/tugas/1")
def hapus_tugas():
    return {"aksi": "menghapus tugas nomor 1"}
