from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class AkunBaru(BaseModel):
    nama: str
    email: str
    kata_sandi: str


class AkunPublik(BaseModel):
    id: int
    nama: str
    email: str


class Profil(BaseModel):
    nama: str
    bio: str | None = None
    kota: str = "Tidak diketahui"


# Basis data tiruan dalam memori; kata sandi di sini hanya contoh, bukan praktik nyata.
akun_db: list[dict] = []
profil_db = {
    "budi": {"nama": "Budi", "kota": "Bandung"},
    "sari": {"nama": "Sari", "bio": None, "kota": "Tidak diketahui"},
}


@app.post("/akun", response_model=AkunPublik, status_code=201)
def buat_akun(data: AkunBaru):
    akun = {"id": len(akun_db) + 1, **data.model_dump()}
    akun_db.append(akun)
    return akun


@app.get("/akun", response_model=list[AkunPublik])
def daftar_akun():
    return akun_db


@app.get("/profil/{nama}", response_model=Profil)
def lihat_profil(nama: str):
    return profil_db[nama]


@app.get("/profil/{nama}/ringkas", response_model=Profil, response_model_exclude_unset=True)
def lihat_profil_ringkas(nama: str):
    return profil_db[nama]


@app.get("/profil/{nama}/tanpa-kota", response_model=Profil, response_model_exclude={"kota"})
def lihat_profil_tanpa_kota(nama: str):
    return profil_db[nama]


@app.get("/rusak", response_model=AkunPublik)
def respons_rusak():
    return {"id": 1, "nama": "Tanpa email"}
