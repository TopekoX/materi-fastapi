"""Mengirim beberapa request /hitung sekaligus dan mengukur waktu totalnya.

Pemakaian: python ukur_paralel.py <port> <jumlah_request>
"""

import sys
import time
from concurrent.futures import ThreadPoolExecutor

import httpx

port = int(sys.argv[1])
jumlah = int(sys.argv[2])
url = f"http://127.0.0.1:{port}/hitung"


def kirim(_):
    return httpx.get(url, timeout=60).json()


mulai = time.perf_counter()
with ThreadPoolExecutor(max_workers=jumlah) as pool:
    hasil = list(pool.map(kirim, range(jumlah)))
total = time.perf_counter() - mulai

print(f"{jumlah} request sekaligus: total {total:.2f} detik")
print(f"lama tiap request di server (detik): {[h['detik'] for h in hasil]}")
print(f"proses berbeda yang melayani: {len({h['pid'] for h in hasil})}")
