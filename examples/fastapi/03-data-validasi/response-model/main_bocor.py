from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Akun(BaseModel):
    nama: str
    email: str
    kata_sandi: str


@app.post("/akun", status_code=201)
def buat_akun(data: Akun):
    return data
