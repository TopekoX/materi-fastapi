from fastapi import FastAPI

app = FastAPI()


@app.get("/tugas/{tugas_id}")
def detail_tugas(tugas_id: int):
    return {"tugas_id": tugas_id, "tipe": type(tugas_id).__name__}


@app.get("/salam/{nama}")
def salam(nama: str):
    return {"pesan": f"Halo, {nama}!"}
