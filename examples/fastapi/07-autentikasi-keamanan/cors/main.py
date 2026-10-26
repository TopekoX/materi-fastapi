from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Daftar origin frontend yang boleh memanggil API ini dari browser.
# Origin = protokol + domain + port.
origin_diizinkan = [
    "http://localhost:3000",
    "https://aplikasi-saya.example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin_diizinkan,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=False,
    max_age=600,
)


@app.get("/tugas")
def daftar_tugas():
    return [{"id": 1, "judul": "Belajar CORS"}]


@app.post("/tugas", status_code=201)
def buat_tugas(judul: str):
    return {"id": 2, "judul": judul}


@app.delete("/tugas/{tugas_id}", status_code=204)
def hapus_tugas(tugas_id: int):
    return None
