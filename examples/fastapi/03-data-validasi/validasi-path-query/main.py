from typing import Annotated

from fastapi import FastAPI, Path, Query

app = FastAPI()


@app.get("/buku/{buku_id}")
def detail_buku(
    buku_id: Annotated[int, Path(title="ID buku", ge=1, le=9999)],
    tampilan: Annotated[str, Query(pattern="^(ringkas|lengkap)$")] = "ringkas",
):
    return {"buku_id": buku_id, "tampilan": tampilan}


@app.get("/buku")
def cari_buku(
    cari: Annotated[
        str | None,
        Query(min_length=2, max_length=30, description="Kata kunci judul"),
    ] = None,
    halaman: Annotated[int, Query(ge=1)] = 1,
    batas: Annotated[int, Query(ge=1, le=50)] = 10,
    tag: Annotated[list[str] | None, Query(max_length=3)] = None,
    urut_berdasarkan: Annotated[str, Query(alias="urut-berdasarkan")] = "judul",
):
    return {
        "cari": cari,
        "halaman": halaman,
        "batas": batas,
        "tag": tag,
        "urut_berdasarkan": urut_berdasarkan,
    }


@app.get("/laporan")
def laporan(tahun: Annotated[int, Query(ge=2000, le=2100)]):
    return {"tahun": tahun}
