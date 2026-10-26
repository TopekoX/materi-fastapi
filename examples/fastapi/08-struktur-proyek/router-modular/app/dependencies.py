from typing import Annotated

from fastapi import Header, HTTPException


def pengguna_saat_ini(x_pengguna: Annotated[str, Header()]) -> str:
    """Pengganti sementara untuk autentikasi (contoh saja, bukan keamanan sungguhan).

    Di aplikasi nyata ini diganti dependency token dari Modul 07.
    """
    if x_pengguna not in {"budi", "sari", "rina"}:
        raise HTTPException(status_code=401, detail="Pengguna tidak dikenal")
    return x_pengguna


def wajib_pengelola(x_pengguna: Annotated[str, Header()]) -> None:
    if x_pengguna != "rina":
        raise HTTPException(status_code=403, detail="Hanya untuk pengelola")
