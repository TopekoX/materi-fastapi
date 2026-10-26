import asyncio
from typing import Annotated

from fastapi import Depends, FastAPI

app = FastAPI()


async def ambil_cuaca() -> dict:
    await asyncio.sleep(0.1)  # pura-pura menunggu layanan luar
    return {"kota": "Bandung", "suhu": 24}


def ambil_zona_waktu() -> str:
    return "WIB"


@app.get("/info")
def info(
    cuaca: Annotated[dict, Depends(ambil_cuaca)],
    zona: Annotated[str, Depends(ambil_zona_waktu)],
):
    return {"cuaca": cuaca, "zona": zona}


@app.get("/info-async")
async def info_async(
    cuaca: Annotated[dict, Depends(ambil_cuaca)],
    zona: Annotated[str, Depends(ambil_zona_waktu)],
):
    return {"cuaca": cuaca, "zona": zona}
