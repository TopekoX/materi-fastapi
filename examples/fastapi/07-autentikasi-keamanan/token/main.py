import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel, Field

# Kunci penandatangan dibaca dari variabel environment, tidak ditulis di kode.
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "Variabel environment SECRET_KEY belum diisi. "
        'Buat kunci dengan: python -c "import secrets; print(secrets.token_hex(32))"'
    )

ALGORITMA = "HS256"
MENIT_KEDALUWARSA = 30

app = FastAPI()
password_hash = PasswordHash.recommended()
HASH_TIRUAN = password_hash.hash("kata-sandi-tiruan")

pengguna_db: dict[str, str] = {}  # nama_pengguna -> hash kata sandi (sementara, di memori)


class PenggunaBaru(BaseModel):
    nama_pengguna: str = Field(min_length=3, max_length=30)
    kata_sandi: str = Field(min_length=8, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str


def buat_token(nama_pengguna: str, berlaku: timedelta) -> str:
    isi = {"sub": nama_pengguna, "exp": datetime.now(timezone.utc) + berlaku}
    return jwt.encode(isi, SECRET_KEY, algorithm=ALGORITMA)


def autentikasi(nama_pengguna: str, kata_sandi: str) -> bool:
    hash_tersimpan = pengguna_db.get(nama_pengguna)
    if hash_tersimpan is None:
        password_hash.verify(kata_sandi, HASH_TIRUAN)  # samakan waktu respons
        return False
    return password_hash.verify(kata_sandi, hash_tersimpan)


@app.post("/daftar", status_code=status.HTTP_201_CREATED)
def daftar(data: PenggunaBaru):
    if data.nama_pengguna in pengguna_db:
        raise HTTPException(status_code=409, detail="Nama pengguna sudah dipakai")
    pengguna_db[data.nama_pengguna] = password_hash.hash(data.kata_sandi)
    return {"nama_pengguna": data.nama_pengguna}


@app.post("/token")
def masuk(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    if not autentikasi(form.username, form.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nama pengguna atau kata sandi salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = buat_token(form.username, timedelta(minutes=MENIT_KEDALUWARSA))
    return Token(access_token=token, token_type="bearer")


@app.get("/periksa-token")
def periksa_token(token: str):
    """Hanya untuk percobaan: membaca isi token. Perlindungan endpoint sungguhan ada di halaman berikutnya."""
    try:
        isi = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMA])
    except InvalidTokenError as galat:
        raise HTTPException(status_code=401, detail=f"Token tidak valid: {type(galat).__name__}")
    return {"sub": isi["sub"], "exp": isi["exp"]}
