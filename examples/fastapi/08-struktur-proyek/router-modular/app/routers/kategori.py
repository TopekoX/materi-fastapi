from fastapi import APIRouter, HTTPException

from ..schemas import Kategori, KategoriBuat

router = APIRouter(prefix="/kategori", tags=["kategori"])

kategori_db: dict[int, Kategori] = {}
id_berikutnya = 1


@router.post("/", response_model=Kategori, status_code=201)
def buat_kategori(data: KategoriBuat):
    global id_berikutnya
    kategori = Kategori(id=id_berikutnya, **data.model_dump())
    kategori_db[kategori.id] = kategori
    id_berikutnya += 1
    return kategori


@router.get("/", response_model=list[Kategori])
def daftar_kategori():
    return list(kategori_db.values())


@router.get("/{kategori_id}", response_model=Kategori)
def ambil_kategori(kategori_id: int):
    kategori = kategori_db.get(kategori_id)
    if kategori is None:
        raise HTTPException(status_code=404, detail="Kategori tidak ditemukan")
    return kategori
