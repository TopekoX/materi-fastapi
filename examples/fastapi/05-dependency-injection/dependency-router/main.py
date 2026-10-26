from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, Request

pengguna_db = {
    "budi": {"nama": "budi", "peran": "anggota", "aktif": True},
    "sari": {"nama": "sari", "peran": "anggota", "aktif": False},
    "rina": {"nama": "rina", "peran": "pengelola", "aktif": True},
}


def catat(request: Request, nama: str) -> None:
    """Hanya untuk percobaan: mencatat urutan dependency pada request ini."""
    if not hasattr(request.state, "jejak"):
        request.state.jejak = []
    request.state.jejak.append(nama)


def dependensi_global(request: Request) -> None:
    catat(request, "global")


def pengguna_saat_ini(request: Request, x_pengguna: Annotated[str, Header()]) -> dict:
    catat(request, "pengguna_saat_ini")
    pengguna = pengguna_db.get(x_pengguna)
    if pengguna is None:
        raise HTTPException(status_code=401, detail="Pengguna tidak dikenal")
    return pengguna


def pengguna_aktif(request: Request, pengguna: Annotated[dict, Depends(pengguna_saat_ini)]) -> dict:
    catat(request, "pengguna_aktif")
    if not pengguna["aktif"]:
        raise HTTPException(status_code=403, detail="Akun tidak aktif")
    return pengguna


def pengelola(request: Request, pengguna: Annotated[dict, Depends(pengguna_aktif)]) -> dict:
    catat(request, "pengelola")
    if pengguna["peran"] != "pengelola":
        raise HTTPException(status_code=403, detail="Hanya untuk pengelola")
    return pengguna


def dependensi_dekorator(request: Request) -> None:
    catat(request, "dekorator")


def dependensi_parameter(request: Request) -> None:
    catat(request, "parameter")


# Router tanpa dependency: terbuka untuk siapa saja
router_publik = APIRouter(prefix="/publik", tags=["publik"])

# Dependency dipasang saat membuat router
router_anggota = APIRouter(
    prefix="/anggota",
    tags=["anggota"],
    dependencies=[Depends(pengguna_aktif)],
)

# Dependency dipasang saat router dimasukkan ke aplikasi (lihat include_router di bawah)
router_admin = APIRouter(prefix="/admin", tags=["admin"])


@router_publik.get("/info")
def info():
    return {"nama": "Perpustakaan", "terbuka": True}


@router_anggota.get("/profil")
def profil(pengguna: Annotated[dict, Depends(pengguna_saat_ini)]):
    return pengguna


@router_anggota.get("/urutan", dependencies=[Depends(dependensi_dekorator)])
def urutan(request: Request, _: Annotated[None, Depends(dependensi_parameter)]):
    return {"jejak": request.state.jejak}


@router_admin.get("/laporan")
def laporan():
    return {"pesan": "Laporan khusus pengelola"}


app = FastAPI(dependencies=[Depends(dependensi_global)])
app.include_router(router_publik)
app.include_router(router_anggota)
app.include_router(router_admin, dependencies=[Depends(pengelola)])
