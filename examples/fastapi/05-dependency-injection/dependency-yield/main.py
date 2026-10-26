from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException

app = FastAPI()

log: list[str] = []  # hanya untuk percobaan: mencatat kejadian berurutan


class Sesi:
    """Sesi tiruan, pengganti koneksi basis data."""

    def __init__(self):
        self.data: dict[int, str] = {}


def buka_koneksi():
    log.append("koneksi dibuka")
    try:
        yield "koneksi"
    finally:
        log.append("koneksi ditutup")


def transaksi(koneksi: Annotated[str, Depends(buka_koneksi)]):
    sesi = Sesi()
    log.append("transaksi mulai")
    try:
        yield sesi
        log.append("commit")
    except Exception:
        log.append("rollback")
        raise
    finally:
        log.append("transaksi selesai")


TransaksiDep = Annotated[Sesi, Depends(transaksi)]


@app.post("/simpan/{nomor}")
def simpan(nomor: int, sesi: TransaksiDep):
    log.append(f"endpoint jalan ({nomor})")
    if nomor == 0:
        raise HTTPException(status_code=400, detail="Nomor tidak boleh 0")
    if nomor < 0:
        return 1 / 0
    sesi.data[nomor] = "tersimpan"
    return {"nomor": nomor, "status": "tersimpan"}


@app.get("/log")
def lihat_log():
    return log


@app.post("/log/reset")
def reset_log():
    log.clear()
    return {"log": log}
