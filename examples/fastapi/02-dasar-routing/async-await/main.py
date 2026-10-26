import asyncio
import time

from fastapi import FastAPI

app = FastAPI()


@app.get("/def-menunggu")
def def_menunggu():
    time.sleep(1)
    return {"jenis": "def biasa, time.sleep(1)"}


@app.get("/async-menunggu")
async def async_menunggu():
    await asyncio.sleep(1)
    return {"jenis": "async def, await asyncio.sleep(1)"}


@app.get("/async-memblokir")
async def async_memblokir():
    time.sleep(1)
    return {"jenis": "async def, time.sleep(1) (memblokir)"}
