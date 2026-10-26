"""Mengirim 12 request POST /kunjungan sekaligus, lalu menampilkan penghitung tiap proses.

Pemakaian: python ukur_kunjungan.py <port>
"""

import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import httpx

port = sys.argv[1]


def kirim(_):
    return httpx.post(f"http://127.0.0.1:{port}/kunjungan", timeout=30).json()


with ThreadPoolExecutor(max_workers=12) as pool:
    hasil = list(pool.map(kirim, range(12)))

tertinggi = defaultdict(int)
for h in hasil:
    tertinggi[h["pid"]] = max(tertinggi[h["pid"]], h["kunjungan"])

print("jumlah request:", len(hasil), "| proses berbeda:", len(tertinggi))
print("penghitung terakhir per proses:", sorted(tertinggi.values()), "| jumlahnya:", sum(tertinggi.values()))
