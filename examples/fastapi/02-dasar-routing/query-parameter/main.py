from fastapi import FastAPI

app = FastAPI()

DAFTAR_TUGAS = [
    {"id": 1, "judul": "Belajar FastAPI", "selesai": True},
    {"id": 2, "judul": "Membuat endpoint pertama", "selesai": True},
    {"id": 3, "judul": "Mempelajari query parameter", "selesai": False},
    {"id": 4, "judul": "Mengerjakan latihan", "selesai": False},
]


@app.get("/tugas")
def daftar_tugas(selesai: bool | None = None, batas: int = 10):
    hasil = DAFTAR_TUGAS
    if selesai is not None:
        hasil = [t for t in hasil if t["selesai"] == selesai]
    hasil = hasil[:batas]
    return {"jumlah": len(hasil), "data": hasil}


@app.get("/cari")
def cari(kata: str):
    hasil = [t for t in DAFTAR_TUGAS if kata.lower() in t["judul"].lower()]
    return {"kata": kata, "hasil": hasil}
