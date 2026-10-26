from typing import Annotated, Literal

from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI()


class Pesanan(BaseModel):
    produk: str
    jumlah: int
    prioritas: Literal["rendah", "normal", "tinggi"] = "normal"
    tag: list[str] = []
    catatan: str | None = None


@app.get("/hitung/{angka}")
def hitung(angka: int, kali: float = 1.0):
    return {"hasil": angka * kali}


@app.get("/cari")
def cari(
    kata: Annotated[str | None, Query(min_length=2)] = None,
    urut: Literal["judul", "tahun"] = "judul",
    label: Annotated[list[str] | None, Query()] = None,
):
    return {"kata": kata, "urut": urut, "label": label}


@app.post("/pesanan")
def buat_pesanan(pesanan: Pesanan):
    return pesanan
