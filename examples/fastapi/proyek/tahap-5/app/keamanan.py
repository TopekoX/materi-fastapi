from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from sqlmodel import select

from .config import get_settings
from .database import SessionDep
from .models import Pengguna

password_hash = PasswordHash.recommended()
HASH_TIRUAN = password_hash.hash("kata-sandi-tiruan")
skema_oauth2 = OAuth2PasswordBearer(tokenUrl="token")


def buat_token(nama_pengguna: str) -> str:
    settings = get_settings()
    isi = {
        "sub": nama_pengguna,
        "exp": datetime.now(timezone.utc) + timedelta(seconds=settings.detik_akses),
    }
    return jwt.encode(isi, settings.secret_key.get_secret_value(), algorithm=settings.algoritma)


def pengguna_saat_ini(token: Annotated[str, Depends(skema_oauth2)], session: SessionDep) -> Pengguna:
    settings = get_settings()
    gagal = HTTPException(
        status_code=401,
        detail="Token tidak valid atau sudah kedaluwarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        isi = jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=[settings.algoritma])
    except InvalidTokenError:
        raise gagal
    nama = isi.get("sub")
    if not nama:
        raise gagal
    pengguna = session.exec(select(Pengguna).where(Pengguna.nama_pengguna == nama)).first()
    if pengguna is None:
        raise gagal
    return pengguna


PenggunaLogin = Annotated[Pengguna, Depends(pengguna_saat_ini)]


def wajib_pengelola(pengguna: PenggunaLogin) -> Pengguna:
    if pengguna.peran != "pengelola":
        raise HTTPException(status_code=403, detail="Hanya untuk pengelola")
    return pengguna


Pengelola = Annotated[Pengguna, Depends(wajib_pengelola)]
