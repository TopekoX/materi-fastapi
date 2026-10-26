from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class TugasTidakDitemukan(Exception):
    def __init__(self, tugas_id: int):
        self.tugas_id = tugas_id


class KategoriTidakDitemukan(Exception):
    def __init__(self, kategori_id: int):
        self.kategori_id = kategori_id


class JudulSudahAda(Exception):
    def __init__(self, judul: str):
        self.judul = judul


class NamaPenggunaSudahAda(Exception):
    def __init__(self, nama: str):
        self.nama = nama


def respons_galat(
    status_code: int, kode: str, pesan: str, rincian: list | None = None, headers: dict | None = None
):
    isi = {"galat": {"kode": kode, "pesan": pesan, "rincian": rincian or []}}
    return JSONResponse(status_code=status_code, content=isi, headers=headers)


def pasang_penangan_error(app: FastAPI) -> None:
    """Mendaftarkan semua exception handler ke aplikasi."""

    @app.exception_handler(TugasTidakDitemukan)
    async def tugas_tidak_ditemukan(request: Request, exc: TugasTidakDitemukan):
        return respons_galat(404, "TUGAS_TIDAK_ADA", f"Tugas dengan id {exc.tugas_id} tidak ditemukan")

    @app.exception_handler(KategoriTidakDitemukan)
    async def kategori_tidak_ditemukan(request: Request, exc: KategoriTidakDitemukan):
        return respons_galat(
            404, "KATEGORI_TIDAK_ADA", f"Kategori dengan id {exc.kategori_id} tidak ditemukan"
        )

    @app.exception_handler(JudulSudahAda)
    async def judul_sudah_ada(request: Request, exc: JudulSudahAda):
        return respons_galat(409, "JUDUL_SUDAH_ADA", f"Judul '{exc.judul}' sudah dipakai")

    @app.exception_handler(NamaPenggunaSudahAda)
    async def nama_pengguna_sudah_ada(request: Request, exc: NamaPenggunaSudahAda):
        return respons_galat(409, "NAMA_PENGGUNA_SUDAH_ADA", f"Nama pengguna '{exc.nama}' sudah dipakai")

    @app.exception_handler(StarletteHTTPException)
    async def http_exception(request: Request, exc: StarletteHTTPException):
        return respons_galat(
            exc.status_code, f"HTTP_{exc.status_code}", str(exc.detail), headers=getattr(exc, "headers", None)
        )

    @app.exception_handler(RequestValidationError)
    async def validasi(request: Request, exc: RequestValidationError):
        rincian = [
            {"field": ".".join(str(b) for b in galat["loc"]), "jenis": galat["type"], "pesan": galat["msg"]}
            for galat in exc.errors()
        ]
        return respons_galat(422, "VALIDASI_GAGAL", "Data yang dikirim tidak valid", rincian)

    @app.exception_handler(Exception)
    async def galat_tak_terduga(request: Request, exc: Exception):
        return respons_galat(500, "GALAT_SERVER", "Terjadi kesalahan pada server")
