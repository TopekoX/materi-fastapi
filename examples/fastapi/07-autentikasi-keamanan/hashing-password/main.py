from fastapi import FastAPI, HTTPException, status
from pwdlib import PasswordHash
from pydantic import BaseModel, Field

app = FastAPI()

password_hash = PasswordHash.recommended()
# Hash tiruan: dipakai agar waktu respons sama, baik pengguna ada maupun tidak
HASH_TIRUAN = password_hash.hash("kata-sandi-tiruan")

# Penyimpanan sementara di memori (basis data baru dipakai di proyek tahap 4)
pengguna_db: dict[str, str] = {}  # nama_pengguna -> hash kata sandi


class PenggunaBaru(BaseModel):
    nama_pengguna: str = Field(min_length=3, max_length=30)
    kata_sandi: str = Field(min_length=8, max_length=128)


class PenggunaPublik(BaseModel):
    nama_pengguna: str


class Kredensial(BaseModel):
    nama_pengguna: str
    kata_sandi: str


@app.post("/daftar", response_model=PenggunaPublik, status_code=status.HTTP_201_CREATED)
def daftar(data: PenggunaBaru):
    if data.nama_pengguna in pengguna_db:
        raise HTTPException(status_code=409, detail="Nama pengguna sudah dipakai")
    pengguna_db[data.nama_pengguna] = password_hash.hash(data.kata_sandi)
    return PenggunaPublik(nama_pengguna=data.nama_pengguna)


@app.post("/periksa-kata-sandi")
def periksa_kata_sandi(data: Kredensial):
    hash_tersimpan = pengguna_db.get(data.nama_pengguna)
    if hash_tersimpan is None:
        # Tetap menghitung hash agar waktu respons tidak membocorkan nama yang ada
        password_hash.verify(data.kata_sandi, HASH_TIRUAN)
        raise HTTPException(status_code=401, detail="Nama pengguna atau kata sandi salah")
    if not password_hash.verify(data.kata_sandi, hash_tersimpan):
        raise HTTPException(status_code=401, detail="Nama pengguna atau kata sandi salah")
    return {"pesan": "Kata sandi cocok"}


@app.get("/debug/hash/{nama_pengguna}")
def lihat_hash(nama_pengguna: str):
    """Hanya untuk percobaan: memperlihatkan bentuk hash tersimpan. Jangan dibuat di aplikasi nyata."""
    hash_tersimpan = pengguna_db.get(nama_pengguna)
    if hash_tersimpan is None:
        raise HTTPException(status_code=404, detail="Pengguna tidak ditemukan")
    return {"hash": hash_tersimpan}
