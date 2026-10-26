import time
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI()

# Hanya untuk percobaan: mencatat urutan middleware pada request ke /halo
jejak: list[str] = []
status_pemeliharaan = {"aktif": False}


def catat(request: Request, kejadian: str) -> None:
    if request.url.path == "/halo":
        jejak.append(kejadian)


# Middleware pertama yang didaftarkan = paling DALAM (paling dekat dengan endpoint)
@app.middleware("http")
async def waktu_proses(request: Request, call_next):
    catat(request, "waktu: masuk")
    mulai = time.perf_counter()
    response = await call_next(request)
    durasi_ms = (time.perf_counter() - mulai) * 1000
    response.headers["X-Waktu-Proses"] = f"{durasi_ms:.1f} ms"
    catat(request, "waktu: keluar")
    return response


@app.middleware("http")
async def id_permintaan(request: Request, call_next):
    catat(request, "id: masuk")
    request.state.request_id = uuid.uuid4().hex[:8]  # bisa dibaca endpoint lewat request.state
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    catat(request, "id: keluar")
    return response


# Middleware terakhir yang didaftarkan = paling LUAR (pertama menerima request)
@app.middleware("http")
async def pemeliharaan(request: Request, call_next):
    catat(request, "pemeliharaan: masuk")
    if status_pemeliharaan["aktif"] and not request.url.path.startswith("/pemeliharaan"):
        # Menjawab langsung tanpa memanggil call_next: endpoint tidak dijalankan
        return JSONResponse(status_code=503, content={"detail": "Sedang dalam pemeliharaan"})
    response = await call_next(request)
    catat(request, "pemeliharaan: keluar")
    return response


@app.get("/halo")
def halo():
    jejak.append("endpoint")
    return {"pesan": "Halo"}


@app.get("/id")
def lihat_id(request: Request):
    return {"request_id": request.state.request_id}


@app.get("/gagal-http")
def gagal_http():
    raise HTTPException(status_code=418, detail="Teko teh")


@app.get("/rusak")
def rusak():
    return 1 / 0


@app.get("/jejak")
def lihat_jejak():
    return jejak


@app.post("/jejak/reset")
def reset_jejak():
    jejak.clear()
    return {"jejak": jejak}


@app.post("/pemeliharaan/{status}")
def atur_pemeliharaan(status: str):
    status_pemeliharaan["aktif"] = status == "on"
    return status_pemeliharaan
