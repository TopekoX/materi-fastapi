import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("Variabel environment SECRET_KEY belum diisi.")

ALGORITMA = "HS256"
app = FastAPI()
password_hash = PasswordHash.recommended()
HASH_TIRUAN = password_hash.hash("kata-sandi-tiruan")

# Scope = nama izin berupa teks. Deskripsinya tampil di dokumentasi otomatis.
skema_oauth2 = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"tugas:baca": "Membaca tugas", "tugas:tulis": "Membuat dan mengubah tugas"},
)

# Scope yang BOLEH dimiliki setiap pengguna (keputusan server, bukan permintaan klien)
pengguna_db = {
    "budi": {"hash": password_hash.hash("sandi-budi-123"), "scope_boleh": {"tugas:baca", "tugas:tulis"}},
    "tamu": {"hash": password_hash.hash("sandi-tamu-456"), "scope_boleh": {"tugas:baca"}},
}


@app.post("/token")
def masuk(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    pengguna = pengguna_db.get(form.username)
    if pengguna is None:
        password_hash.verify(form.password, HASH_TIRUAN)
        sah = False
    else:
        sah = password_hash.verify(form.password, pengguna["hash"])
    if not sah:
        raise HTTPException(status_code=401, detail="Nama pengguna atau kata sandi salah",
                            headers={"WWW-Authenticate": "Bearer"})
    # Hanya scope yang diminta DAN diizinkan untuk pengguna ini yang masuk ke token
    diberikan = [s for s in form.scopes if s in pengguna["scope_boleh"]]
    isi = {
        "sub": form.username,
        "scope": " ".join(diberikan),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    return {"access_token": jwt.encode(isi, SECRET_KEY, algorithm=ALGORITMA), "token_type": "bearer",
            "scope": " ".join(diberikan)}


def pengguna_dengan_scope(
    scope_dibutuhkan: SecurityScopes, token: Annotated[str, Depends(skema_oauth2)]
) -> str:
    nilai_header = f'Bearer scope="{scope_dibutuhkan.scope_str}"' if scope_dibutuhkan.scopes else "Bearer"
    try:
        isi = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMA])
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token tidak valid atau sudah kedaluwarsa",
                            headers={"WWW-Authenticate": nilai_header})
    scope_token = isi.get("scope", "").split()
    for scope in scope_dibutuhkan.scopes:
        if scope not in scope_token:
            raise HTTPException(status_code=403, detail=f"Butuh scope: {scope}",
                                headers={"WWW-Authenticate": nilai_header})
    return isi["sub"]


@app.get("/tugas")
def baca_tugas(nama: Annotated[str, Security(pengguna_dengan_scope, scopes=["tugas:baca"])]):
    return {"untuk": nama, "tugas": ["Belajar scope"]}


@app.post("/tugas", status_code=201)
def tulis_tugas(nama: Annotated[str, Security(pengguna_dengan_scope, scopes=["tugas:tulis"])]):
    return {"dibuat_oleh": nama}
