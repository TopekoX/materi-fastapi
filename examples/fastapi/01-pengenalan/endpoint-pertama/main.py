from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def halaman_utama():
    return {"pesan": "Halo, FastAPI!"}


@app.get("/tentang")
def tentang():
    return {"nama": "Belajar FastAPI", "modul": 1}
