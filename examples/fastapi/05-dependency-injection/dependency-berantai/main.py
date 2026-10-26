from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI()

pengguna_db = {
    "budi": {"nama": "budi", "peran": "anggota", "aktif": True},
    "sari": {"nama": "sari", "peran": "anggota", "aktif": False},
    "rina": {"nama": "rina", "peran": "pengelola", "aktif": True},
}

jejak: list[str] = []  # hanya untuk percobaan: mencatat dependency yang dijalankan


# Tingkat 1: siapa yang memanggil?
def pengguna_saat_ini(x_pengguna: Annotated[str, Header()]) -> dict:
    jejak.append("pengguna_saat_ini")
    pengguna = pengguna_db.get(x_pengguna)
    if pengguna is None:
        raise HTTPException(status_code=401, detail="Pengguna tidak dikenal")
    return pengguna


# Tingkat 2: bergantung pada tingkat 1
def pengguna_aktif(pengguna: Annotated[dict, Depends(pengguna_saat_ini)]) -> dict:
    jejak.append("pengguna_aktif")
    if not pengguna["aktif"]:
        raise HTTPException(status_code=403, detail="Akun tidak aktif")
    return pengguna


# Tingkat 3: bergantung pada tingkat 2
def pengelola(pengguna: Annotated[dict, Depends(pengguna_aktif)]) -> dict:
    jejak.append("pengelola")
    if pengguna["peran"] != "pengelola":
        raise HTTPException(status_code=403, detail="Hanya untuk pengelola")
    return pengguna


@app.get("/profil")
def profil(pengguna: Annotated[dict, Depends(pengguna_saat_ini)]):
    return pengguna


@app.post("/pinjam")
def pinjam(pengguna: Annotated[dict, Depends(pengguna_aktif)]):
    return {"pesan": f"{pengguna['nama']} berhasil meminjam"}


@app.get("/laporan")
def laporan(pengguna: Annotated[dict, Depends(pengelola)]):
    return {"pesan": f"Laporan untuk {pengguna['nama']}"}


# Dependency yang sama dipakai dua kali dalam satu request
@app.get("/ganda")
def ganda(
    a: Annotated[dict, Depends(pengguna_saat_ini)],
    b: Annotated[dict, Depends(pengguna_aktif)],
):
    jumlah = jejak.count("pengguna_saat_ini")
    return {"a": a["nama"], "b": b["nama"], "jejak": list(jejak), "jumlah_pengguna_saat_ini": jumlah}


@app.get("/ganda-segar")
def ganda_segar(
    a: Annotated[dict, Depends(pengguna_saat_ini)],
    b: Annotated[dict, Depends(pengguna_saat_ini, use_cache=False)],
):
    return {"jejak": list(jejak)}


@app.get("/jejak/reset")
def reset_jejak():
    jejak.clear()
    return {"jejak": jejak}
