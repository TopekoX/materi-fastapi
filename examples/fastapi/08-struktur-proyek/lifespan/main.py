from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request

BERKAS_LOG = Path("lifespan.log")


def catat(pesan: str) -> None:
    waktu = datetime.now().strftime("%H:%M:%S")
    with BERKAS_LOG.open("a", encoding="utf-8") as berkas:
        berkas.write(f"[{waktu}] {pesan}\n")


class SumberDaya:
    """Pengganti sumber daya nyata, misalnya koneksi basis data atau klien HTTP."""

    def __init__(self, nama: str):
        self.nama = nama
        self.terbuka = False

    def buka(self) -> None:
        self.terbuka = True
        catat(f"{self.nama}: dibuka")

    def tutup(self) -> None:
        self.terbuka = False
        catat(f"{self.nama}: ditutup")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Kode SEBELUM yield: dijalankan sekali saat aplikasi mulai ---
    catat("startup: mulai")
    sumber_daya = SumberDaya("koneksi")
    sumber_daya.buka()
    app.state.sumber_daya = sumber_daya  # dibagikan ke seluruh aplikasi lewat app.state
    catat("startup: selesai, aplikasi siap menerima request")

    try:
        yield  # aplikasi berjalan dan melayani request di sini
    finally:
        # --- Kode SESUDAH yield: dijalankan sekali saat aplikasi berhenti ---
        catat("shutdown: mulai")
        sumber_daya.tutup()
        catat("shutdown: selesai")


app = FastAPI(lifespan=lifespan)


@app.get("/status")
def status(request: Request):
    sumber_daya: SumberDaya = request.app.state.sumber_daya
    return {"sumber_daya": sumber_daya.nama, "terbuka": sumber_daya.terbuka}


@app.get("/log")
def lihat_log():
    if not BERKAS_LOG.exists():
        return []
    return BERKAS_LOG.read_text(encoding="utf-8").splitlines()


@app.get("/gagal")
def gagal(request: Request):
    # Endpoint yang error: lifespan tidak ikut terganggu
    raise HTTPException(status_code=500, detail="Sengaja gagal")
