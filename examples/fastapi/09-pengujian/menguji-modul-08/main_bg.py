import time
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import BackgroundTasks, Depends, FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

BERKAS_LOG = Path("notifikasi.log")


class TugasBaru(BaseModel):
    judul: str = Field(min_length=3, max_length=100)
    email: str


def tulis_log(baris: str) -> None:
    waktu = datetime.now().strftime("%H:%M:%S")
    with BERKAS_LOG.open("a", encoding="utf-8") as berkas:
        berkas.write(f"[{waktu}] {baris}\n")


def kirim_notifikasi(email: str, judul: str) -> None:
    """Pura-pura mengirim email: butuh waktu 2 detik."""
    time.sleep(2)
    tulis_log(f"email terkirim ke {email}: tugas '{judul}' dibuat")


def notifikasi_gagal(email: str) -> None:
    raise RuntimeError(f"gagal mengirim email ke {email}")


# Dependency yang ikut menambah tugas latar belakang
def catat_akses(background_tasks: BackgroundTasks) -> None:
    background_tasks.add_task(tulis_log, "akses: POST /tugas dicatat oleh dependency")


@app.post("/tugas", status_code=201)
def buat_tugas(
    data: TugasBaru,
    background_tasks: BackgroundTasks,
    _: Annotated[None, Depends(catat_akses)],
):
    # Response dikirim dulu; kirim_notifikasi berjalan SETELAH response
    background_tasks.add_task(kirim_notifikasi, data.email, data.judul)
    return {"pesan": "Tugas dibuat", "judul": data.judul}


@app.post("/tugas-lambat", status_code=201)
def buat_tugas_lambat(data: TugasBaru):
    # Pembanding: pekerjaan yang sama dijalankan di dalam request, klien harus menunggu
    kirim_notifikasi(data.email, data.judul)
    return {"pesan": "Tugas dibuat", "judul": data.judul}


@app.post("/tugas-gagal", status_code=201)
def buat_tugas_gagal(data: TugasBaru, background_tasks: BackgroundTasks):
    background_tasks.add_task(notifikasi_gagal, data.email)
    return {"pesan": "Tugas dibuat", "judul": data.judul}


@app.get("/log")
def lihat_log():
    if not BERKAS_LOG.exists():
        return []
    return BERKAS_LOG.read_text(encoding="utf-8").splitlines()


@app.post("/log/reset")
def reset_log():
    BERKAS_LOG.unlink(missing_ok=True)
    return {"log": []}
