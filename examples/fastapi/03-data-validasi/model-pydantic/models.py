from pydantic import BaseModel


class Alamat(BaseModel):
    kota: str
    kode_pos: str | None = None


class Pengguna(BaseModel):
    nama: str
    umur: int
    aktif: bool = True
    hobi: list[str] = []
    alamat: Alamat | None = None
