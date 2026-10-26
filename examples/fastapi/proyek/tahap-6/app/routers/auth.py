from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from ..database import SessionDep
from ..errors import NamaPenggunaSudahAda
from ..keamanan import HASH_TIRUAN, PenggunaLogin, buat_token, password_hash
from ..models import Pengguna, PenggunaBuat, PenggunaPublik, Token

router = APIRouter(tags=["autentikasi"])


@router.post("/daftar", response_model=PenggunaPublik, status_code=status.HTTP_201_CREATED)
def daftar(data: PenggunaBuat, session: SessionDep):
    ada = session.exec(select(Pengguna).where(Pengguna.nama_pengguna == data.nama_pengguna)).first()
    if ada is not None:
        raise NamaPenggunaSudahAda(data.nama_pengguna)
    pengguna = Pengguna(
        nama_pengguna=data.nama_pengguna,
        hash_kata_sandi=password_hash.hash(data.kata_sandi),
        peran="anggota",
    )
    session.add(pengguna)
    session.commit()
    session.refresh(pengguna)
    return pengguna


@router.post("/token", response_model=Token)
def masuk(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    pengguna = session.exec(select(Pengguna).where(Pengguna.nama_pengguna == form.username)).first()
    if pengguna is None:
        password_hash.verify(form.password, HASH_TIRUAN)  # samakan waktu respons
        sah = False
    else:
        sah = password_hash.verify(form.password, pengguna.hash_kata_sandi)
    if not sah:
        raise HTTPException(
            status_code=401,
            detail="Nama pengguna atau kata sandi salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=buat_token(pengguna.nama_pengguna), token_type="bearer")


@router.get("/saya", response_model=PenggunaPublik)
def profil_saya(pengguna: PenggunaLogin):
    return pengguna
