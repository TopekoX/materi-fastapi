from pydantic import BaseModel, Field


class KategoriBuat(BaseModel):
    nama: str = Field(min_length=2, max_length=50)


class Kategori(KategoriBuat):
    id: int


class TugasBuat(BaseModel):
    judul: str = Field(min_length=3, max_length=100)
    selesai: bool = False


class Tugas(TugasBuat):
    id: int
    pemilik: str
