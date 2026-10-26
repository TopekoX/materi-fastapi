from fastapi import FastAPI

app = FastAPI(
    title="Belajar FastAPI",
    description="Aplikasi pertama dari materi Belajar FastAPI.",
    version="0.1.0",
)


@app.get("/")
def halaman_utama():
    return {"pesan": "Aplikasi pertama berjalan!"}


@app.get("/kesehatan")
def kesehatan():
    return {"status": "ok"}
