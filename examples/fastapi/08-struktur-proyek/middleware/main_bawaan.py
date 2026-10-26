from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# Mengompres response yang lebih besar dari 500 byte, bila klien menyatakan mendukung gzip
app.add_middleware(GZipMiddleware, minimum_size=500)

# Hanya menerima request yang header Host-nya ada dalam daftar
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])


@app.get("/kecil")
def kecil():
    return {"pesan": "singkat"}


@app.get("/besar")
def besar():
    return {"data": ["tugas nomor " + str(n) for n in range(300)]}
