import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel, Field

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "Variabel environment SECRET_KEY belum diisi. "
        'Buat kunci dengan: python -c "import secrets; print(secrets.token_hex(32))"'
    )

ALGORITMA = "HS256"
app = FastAPI()
password_hash = PasswordHash.recommended()
HASH_TIRUAN = password_hash.hash("kata-sandi-tiruan")
skema_oauth2 = OAuth2PasswordBearer(tokenUrl="token")

# Data contoh untuk percobaan. Kata sandi di sini hanya untuk demo, jangan ditiru di aplikasi nyata.
pengguna_db: dict[str, dict] = {
    "budi": {"hash": password_hash.hash("sandi-budi-123"), "peran": "anggota"},
    "sari": {"hash": password_hash.hash("sandi-sari-456"), "peran": "anggota"},
    "rina": {"hash": password_hash.hash("sandi-rina-789"), "peran": "pengelola"},
}

tugas_db: dict[int, dict] = {
    1: {"id": 1, "judul": "Tugas milik Budi", "pemilik": "budi"},
    2: {"id": 2, "judul": "Tugas milik Sari", "pemilik": "sari"},
}
id_berikutnya = 3


class Pengguna(BaseModel):
    nama_pengguna: str
    peran: str


class TugasBaru(BaseModel):
    judul: str = Field(min_length=3, max_length=100)


class Token(BaseModel):
    access_token: str
    token_type: str


# --- Autentikasi (sama seperti halaman sebelumnya) ----------------------------
@app.post("/token")
def masuk(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    pengguna = pengguna_db.get(form.username)
    if pengguna is None:
        password_hash.verify(form.password, HASH_TIRUAN)
        sah = False
    else:
        sah = password_hash.verify(form.password, pengguna["hash"])
    if not sah:
        raise HTTPException(
            status_code=401,
            detail="Nama pengguna atau kata sandi salah",
            headers={"WWW-Authenticate": "Bearer"},
        )
    isi = {"sub": form.username, "exp": datetime.now(timezone.utc) + timedelta(minutes=30)}
    return Token(access_token=jwt.encode(isi, SECRET_KEY, algorithm=ALGORITMA), token_type="bearer")


def pengguna_saat_ini(token: Annotated[str, Depends(skema_oauth2)]) -> Pengguna:
    gagal = HTTPException(
        status_code=401,
        detail="Token tidak valid atau sudah kedaluwarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        isi = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMA])
    except InvalidTokenError:
        raise gagal
    nama = isi.get("sub")
    pengguna = pengguna_db.get(nama) if nama else None
    if pengguna is None:
        raise gagal
    return Pengguna(nama_pengguna=nama, peran=pengguna["peran"])


PenggunaLogin = Annotated[Pengguna, Depends(pengguna_saat_ini)]


# --- Otorisasi 1: berdasarkan peran ------------------------------------------
def wajib_peran(*peran_diizinkan: str):
    """Membuat dependency yang hanya meloloskan pengguna dengan salah satu peran yang diizinkan."""

    def periksa(pengguna: PenggunaLogin) -> Pengguna:
        if pengguna.peran not in peran_diizinkan:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Hanya untuk peran: {', '.join(peran_diizinkan)}",
            )
        return pengguna

    return periksa


@app.get("/laporan")
def laporan(pengelola: Annotated[Pengguna, Depends(wajib_peran("pengelola"))]):
    return {"pesan": f"Laporan untuk {pengelola.nama_pengguna}", "jumlah_tugas": len(tugas_db)}


# --- Otorisasi 2: berdasarkan kepemilikan data ----------------------------------
def tugas_yang_boleh_diubah(tugas_id: int, pengguna: PenggunaLogin) -> dict:
    tugas = tugas_db.get(tugas_id)
    if tugas is None:
        raise HTTPException(status_code=404, detail="Tugas tidak ditemukan")
    if tugas["pemilik"] != pengguna.nama_pengguna and pengguna.peran != "pengelola":
        raise HTTPException(status_code=403, detail="Tugas ini bukan milikmu")
    return tugas


@app.get("/tugas")
def daftar_tugas_saya(pengguna: PenggunaLogin):
    """Pengelola melihat semua tugas; anggota hanya melihat tugasnya sendiri."""
    if pengguna.peran == "pengelola":
        return list(tugas_db.values())
    return [t for t in tugas_db.values() if t["pemilik"] == pengguna.nama_pengguna]


@app.post("/tugas", status_code=201)
def buat_tugas(data: TugasBaru, pengguna: PenggunaLogin):
    global id_berikutnya
    tugas = {"id": id_berikutnya, "judul": data.judul, "pemilik": pengguna.nama_pengguna}
    tugas_db[id_berikutnya] = tugas
    id_berikutnya += 1
    return tugas


@app.put("/tugas/{tugas_id}")
def ganti_tugas(data: TugasBaru, tugas: Annotated[dict, Depends(tugas_yang_boleh_diubah)]):
    tugas["judul"] = data.judul
    return tugas


@app.delete("/tugas/{tugas_id}", status_code=204)
def hapus_tugas(tugas: Annotated[dict, Depends(tugas_yang_boleh_diubah)]):
    del tugas_db[tugas["id"]]
