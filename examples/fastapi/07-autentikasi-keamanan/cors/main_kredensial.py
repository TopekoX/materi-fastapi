from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Dengan allow_credentials=True (cookie atau header Authorization boleh ikut),
# sebutkan origin, method, dan header SATU PER SATU. Jangan memakai "*".
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/profil")
def profil():
    return {"nama": "budi"}
