from typing import Annotated

from fastapi import FastAPI, Header, Path, Query
from pydantic import BaseModel, Field

app = FastAPI()


class Alamat(BaseModel):
    kota: str = Field(min_length=2)
    kode_pos: str = Field(pattern=r"^\d{5}$")


class Pendaftaran(BaseModel):
    nama: str = Field(min_length=3)
    umur: int = Field(ge=17)
    alamat: Alamat
    hobi: list[str] = []


@app.post("/kelas/{kelas_id}/daftar", status_code=201)
def daftar(
    kelas_id: Annotated[int, Path(ge=1)],
    data: Pendaftaran,
    sumber: Annotated[str, Query(min_length=2)] = "web",
    x_versi: Annotated[int, Header(ge=1)] = 1,
):
    return {"kelas_id": kelas_id, "sumber": sumber, "x_versi": x_versi, "data": data}
