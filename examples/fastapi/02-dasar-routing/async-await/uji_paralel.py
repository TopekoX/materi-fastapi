import asyncio
import sys
import time

import httpx

ALAMAT = "http://127.0.0.1:8000"
JUMLAH = 3
PATH = ["/def-menunggu", "/async-menunggu", "/async-memblokir"]


async def ukur(klien, path):
    mulai = time.perf_counter()
    hasil = await asyncio.gather(*[klien.get(path) for _ in range(JUMLAH)])
    total = time.perf_counter() - mulai
    status = {r.status_code for r in hasil}
    print(f"{path:<18} {JUMLAH} request bersamaan -> {total:.2f} detik, status {status}")


async def main():
    async with httpx.AsyncClient(base_url=ALAMAT, timeout=30) as klien:
        for path in PATH:
            await ukur(klien, path)


if len(sys.argv) > 1:
    ALAMAT = sys.argv[1]
asyncio.run(main())
