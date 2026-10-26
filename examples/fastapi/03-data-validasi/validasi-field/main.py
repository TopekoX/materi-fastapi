from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator

app = FastAPI()


class Pendaftaran(BaseModel):
    nama: str = Field(min_length=3, max_length=30, description="Nama lengkap")
    umur: int = Field(ge=17, le=100)
    kode_kelas: str = Field(pattern=r"^[A-Z]{2}\d{3}$", description="Contoh: IF101")
    nilai_awal: float = Field(default=0, ge=0, le=100)
    minat: list[str] = Field(default=[], max_length=3)

    @field_validator("nama")
    @classmethod
    def nama_tanpa_angka(cls, nilai: str) -> str:
        if any(huruf.isdigit() for huruf in nilai):
            raise ValueError("nama tidak boleh mengandung angka")
        return nilai.title()


@app.post("/pendaftaran", status_code=201)
def daftar(data: Pendaftaran):
    return data.model_dump()
