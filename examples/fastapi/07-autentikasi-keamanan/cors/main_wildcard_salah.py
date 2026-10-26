from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Kombinasi yang dilarang dokumentasi FastAPI: wildcard bersama kredensial.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/profil")
def profil():
    return {"nama": "budi"}
