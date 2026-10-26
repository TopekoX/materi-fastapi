from fastapi import FastAPI

app = FastAPI(title="Katalog Buku", version="0.1.0")

DAFTAR_BUKU = [
    {"id": 1, "judul": "Belajar Python Dasar", "penulis": "Sari Dewi", "tahun": 2019},
    {"id": 2, "judul": "Memahami HTTP", "penulis": "Budi Santoso", "tahun": 2021},
    {"id": 3, "judul": "FastAPI untuk Pemula", "penulis": "Sari Dewi", "tahun": 2023},
    {"id": 4, "judul": "Dasar Basis Data", "penulis": "Rahmat Hidayat", "tahun": 2018},
]


@app.get("/status")
async def status():
    return {"status": "ok", "jumlah_buku": len(DAFTAR_BUKU)}


@app.get("/buku")
def daftar_buku(
    penulis: str | None = None,
    terbit_setelah: int | None = None,
    batas: int = 10,
):
    hasil = DAFTAR_BUKU
    if penulis is not None:
        hasil = [b for b in hasil if b["penulis"].lower() == penulis.lower()]
    if terbit_setelah is not None:
        hasil = [b for b in hasil if b["tahun"] > terbit_setelah]
    hasil = hasil[:batas]
    return {"jumlah": len(hasil), "data": hasil}


@app.get("/buku/terbaru")
def buku_terbaru():
    return max(DAFTAR_BUKU, key=lambda b: b["tahun"])


@app.get("/buku/{buku_id}")
def detail_buku(buku_id: int):
    for buku in DAFTAR_BUKU:
        if buku["id"] == buku_id:
            return buku
    return {"pesan": "Buku tidak ditemukan"}
