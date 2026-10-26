from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/buku/{buku_id}")
def lihat_buku(buku_id: int):
    return HTTPException(status_code=404, detail="Tidak ditemukan")
