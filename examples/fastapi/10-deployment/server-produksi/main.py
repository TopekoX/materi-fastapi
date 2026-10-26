import os
import time

from fastapi import FastAPI

app = FastAPI()


@app.get("/info")
def info():
    """Menunjukkan proses mana yang melayani request ini."""
    return {"pid": os.getpid()}


kunjungan = 0  # penghitung di memori: SETIAP proses punya salinannya sendiri


@app.post("/kunjungan")
def catat_kunjungan():
    global kunjungan
    kunjungan += 1
    return {"pid": os.getpid(), "kunjungan": kunjungan}


@app.get("/hitung")
def hitung(n: int = 20_000_000):
    """Pekerjaan yang benar-benar memakai CPU dengan jumlah langkah tetap (bukan menunggu).

    Mensimulasikan komputasi berat. Lama eksekusi bergantung pada kecepatan mesin.
    """
    mulai = time.perf_counter()
    total = 0
    for i in range(n):
        total += i * i
    return {"pid": os.getpid(), "detik": round(time.perf_counter() - mulai, 2)}
