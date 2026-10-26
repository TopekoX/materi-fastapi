from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class AkunDasar(BaseModel):
    nama: str
    email: str


class AkunBaru(AkunDasar):
    kata_sandi: str


@app.post("/akun", status_code=201)
def buat_akun(data: AkunBaru) -> AkunDasar:
    return data
