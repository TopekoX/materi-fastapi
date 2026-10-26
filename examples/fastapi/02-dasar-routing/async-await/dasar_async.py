import asyncio
import time


async def siapkan(nama):
    await asyncio.sleep(1)
    return f"{nama} siap"


async def satu_per_satu():
    mulai = time.perf_counter()
    for nama in ["nasi", "sayur", "teh"]:
        print(await siapkan(nama))
    print(f"satu per satu: {time.perf_counter() - mulai:.2f} detik")


async def bersamaan():
    mulai = time.perf_counter()
    hasil = await asyncio.gather(siapkan("nasi"), siapkan("sayur"), siapkan("teh"))
    print(hasil)
    print(f"bersamaan: {time.perf_counter() - mulai:.2f} detik")


asyncio.run(satu_per_satu())
asyncio.run(bersamaan())
