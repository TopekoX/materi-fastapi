from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# --- Konfigurasi sebagai dependency ---------------------------------------------


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TUGASKU_")

    nama_aplikasi: str = "TugasKu"
    batas_tugas: int = Field(default=100, ge=1)


@lru_cache
def get_settings() -> Settings:
    return Settings()


# --- Autentikasi sebagai dependency (pengganti sederhana; bukan keamanan sungguhan) ----


def pengguna_saat_ini(x_pengguna: Annotated[str, Header()]) -> str:
    if x_pengguna not in {"budi", "sari"}:
        raise HTTPException(status_code=401, detail="Pengguna tidak dikenal")
    return x_pengguna


# --- Layanan luar sebagai dependency: kirim email -------------------------------------


class PengirimEmail:
    """Pengirim email sungguhan. Dalam contoh ini hanya mensimulasikan kegagalan."""

    def kirim(self, tujuan: str, isi: str) -> None:
        raise RuntimeError("Server email tidak dapat dihubungi")  # layanan luar yang tidak ada


def get_pengirim() -> PengirimEmail:
    return PengirimEmail()


# --- Aplikasi ----------------------------------------------------------------------------

app = FastAPI()
tugas_db: list[dict] = []


class TugasBaru(BaseModel):
    judul: str = Field(min_length=3, max_length=100)


@app.get("/info")
def info(settings: Annotated[Settings, Depends(get_settings)]):
    return {"nama_aplikasi": settings.nama_aplikasi, "batas_tugas": settings.batas_tugas}


@app.get("/saya")
def saya(pengguna: Annotated[str, Depends(pengguna_saat_ini)]):
    return {"pengguna": pengguna}


@app.post("/tugas", status_code=201)
def buat_tugas(
    data: TugasBaru,
    pengguna: Annotated[str, Depends(pengguna_saat_ini)],
    settings: Annotated[Settings, Depends(get_settings)],
    pengirim: Annotated[PengirimEmail, Depends(get_pengirim)],
):
    if len(tugas_db) >= settings.batas_tugas:
        raise HTTPException(status_code=409, detail="Batas jumlah tugas tercapai")
    tugas = {"id": len(tugas_db) + 1, "judul": data.judul, "pemilik": pengguna}
    tugas_db.append(tugas)
    pengirim.kirim(f"{pengguna}@contoh.id", f"Tugas '{data.judul}' dibuat")
    return tugas
