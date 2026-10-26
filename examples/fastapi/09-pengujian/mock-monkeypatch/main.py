import os
from datetime import datetime

import httpx
from fastapi import FastAPI, HTTPException

from layanan import ambil_kurs  # nama ambil_kurs kini ada di modul main

app = FastAPI()


def waktu_sekarang() -> datetime:
    return datetime.now()


@app.get("/salam")
def salam():
    jam = waktu_sekarang().hour
    if jam < 11:
        sapaan = "Selamat pagi"
    elif jam < 15:
        sapaan = "Selamat siang"
    elif jam < 18:
        sapaan = "Selamat sore"
    else:
        sapaan = "Selamat malam"
    return {"sapaan": sapaan}


@app.get("/kurs")
def konversi(jumlah: float):
    try:
        kurs = ambil_kurs()
    except httpx.HTTPError:
        raise HTTPException(status_code=503, detail="Layanan kurs tidak tersedia")
    return {"jumlah": jumlah, "kurs": kurs, "hasil": jumlah * kurs}


@app.get("/mode")
def mode():
    # Dibaca setiap kali dipanggil, bukan saat impor, sehingga bisa diubah di pengujian
    return {"mode": os.environ.get("TUGASKU_MODE", "produksi")}
