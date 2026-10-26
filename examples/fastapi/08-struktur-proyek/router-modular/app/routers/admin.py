from fastapi import APIRouter

from . import kategori, tugas

# Router tanpa dependency sendiri; syaratnya (wajib pengelola) dipasang saat router di-include di main.py.
router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/ringkasan")
def ringkasan():
    return {
        "jumlah_tugas": len(tugas.tugas_db),
        "jumlah_kategori": len(kategori.kategori_db),
    }
