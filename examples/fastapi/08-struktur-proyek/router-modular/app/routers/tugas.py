from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from ..dependencies import pengguna_saat_ini
from ..schemas import Tugas, TugasBuat

# Router ini hanya mengurus tugas. Prefix, tags, dan dependency berlaku untuk semua endpoint di sini.
router = APIRouter(
    prefix="/tugas",
    tags=["tugas"],
    responses={404: {"description": "Tugas tidak ditemukan"}},
)

tugas_db: dict[int, Tugas] = {}
id_berikutnya = 1

PenggunaLogin = Annotated[str, Depends(pengguna_saat_ini)]


@router.post("/", response_model=Tugas, status_code=201)
def buat_tugas(data: TugasBuat, pengguna: PenggunaLogin):
    global id_berikutnya
    tugas = Tugas(id=id_berikutnya, pemilik=pengguna, **data.model_dump())
    tugas_db[tugas.id] = tugas
    id_berikutnya += 1
    return tugas


@router.get("/", response_model=list[Tugas])
def daftar_tugas(pengguna: PenggunaLogin):
    return [t for t in tugas_db.values() if t.pemilik == pengguna]


@router.get("/{tugas_id}", response_model=Tugas)
def ambil_tugas(tugas_id: int, pengguna: PenggunaLogin):
    tugas = tugas_db.get(tugas_id)
    if tugas is None or tugas.pemilik != pengguna:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")
    return tugas
