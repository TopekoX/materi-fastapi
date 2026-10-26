from fastapi import FastAPI

app = FastAPI()


@app.delete("/catatan/{nomor}", status_code=204)
def hapus_catatan(nomor: int):
    return {"dihapus": nomor}
