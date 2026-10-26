from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Contoh: sumber daya wajib tidak bisa dibuka (misalnya basis data tidak tersedia)
    raise RuntimeError("tidak bisa membuka koneksi basis data")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def beranda():
    return {"pesan": "tidak akan pernah sampai di sini"}
