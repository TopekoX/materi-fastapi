from fastapi import APIRouter, status
from sqlmodel import select

from ..database import SessionDep
from ..keamanan import Pengelola, PenggunaLogin
from ..models import Kategori, KategoriBuat, KategoriPublik

router = APIRouter(prefix="/kategori", tags=["kategori"])


@router.post("", response_model=KategoriPublik, status_code=status.HTTP_201_CREATED)
def buat_kategori(data: KategoriBuat, pengelola: Pengelola, session: SessionDep):
    kategori = Kategori.model_validate(data)
    session.add(kategori)
    session.commit()
    session.refresh(kategori)
    return kategori


@router.get("", response_model=list[KategoriPublik])
def daftar_kategori(pengguna: PenggunaLogin, session: SessionDep):
    return session.exec(select(Kategori)).all()
