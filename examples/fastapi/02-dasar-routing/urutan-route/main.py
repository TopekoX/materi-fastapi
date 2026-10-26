from fastapi import FastAPI

app = FastAPI()


@app.get("/pengguna/saya")
def pengguna_saya():
    return {"pengguna": "pengguna yang sedang masuk"}


@app.get("/pengguna/{pengguna_id}")
def detail_pengguna(pengguna_id: int):
    return {"pengguna_id": pengguna_id}
