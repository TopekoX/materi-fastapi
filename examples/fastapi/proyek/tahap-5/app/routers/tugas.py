from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session, col, select

from ..database import SessionDep
from ..errors import JudulSudahAda, KategoriTidakDitemukan, TugasTidakDitemukan
from ..keamanan import PenggunaLogin
from ..models import Kategori, Tugas, TugasBuat, TugasDenganKategori, TugasPublik, TugasUbah

router = APIRouter(prefix="/tugas", tags=["tugas"])

IdTugas = Annotated[int, Path(ge=1, title="ID tugas")]


def pastikan_kategori_ada(session: Session, kategori_id: int | None) -> None:
    if kategori_id is not None and session.get(Kategori, kategori_id) is None:
        raise KategoriTidakDitemukan(kategori_id)


def pastikan_judul_unik(session: Session, pemilik_id: int | None, judul: str, abaikan_id: int | None = None) -> None:
    """Judul harus unik per pemilik, tanpa membedakan huruf besar-kecil."""
    pernyataan = select(Tugas).where(Tugas.pemilik_id == pemilik_id, col(Tugas.judul).ilike(judul))
    for tugas in session.exec(pernyataan).all():
        if tugas.id != abaikan_id:
            raise JudulSudahAda(judul)


def tugas_yang_boleh_diakses(tugas_id: IdTugas, pengguna: PenggunaLogin, session: SessionDep) -> Tugas:
    tugas = session.get(Tugas, tugas_id)
    if tugas is None:
        raise TugasTidakDitemukan(tugas_id)
    if tugas.pemilik_id != pengguna.id and pengguna.peran != "pengelola":
        raise HTTPException(status_code=403, detail="Tugas ini bukan milikmu")
    return tugas


TugasDiakses = Annotated[Tugas, Depends(tugas_yang_boleh_diakses)]


@router.post("", response_model=TugasPublik, status_code=status.HTTP_201_CREATED)
def buat_tugas(data: TugasBuat, pengguna: PenggunaLogin, session: SessionDep):
    pastikan_kategori_ada(session, data.kategori_id)
    pastikan_judul_unik(session, pengguna.id, data.judul)
    tugas = Tugas.model_validate(data, update={"pemilik_id": pengguna.id})
    session.add(tugas)
    session.commit()
    session.refresh(tugas)
    return tugas


@router.get("", response_model=list[TugasPublik])
def daftar_tugas(
    pengguna: PenggunaLogin,
    session: SessionDep,
    selesai: bool | None = None,
    kategori_id: int | None = None,
    cari: Annotated[str | None, Query(min_length=2, max_length=50)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
):
    pernyataan = select(Tugas)
    if pengguna.peran != "pengelola":
        pernyataan = pernyataan.where(Tugas.pemilik_id == pengguna.id)
    if selesai is not None:
        pernyataan = pernyataan.where(Tugas.selesai == selesai)
    if kategori_id is not None:
        pernyataan = pernyataan.where(Tugas.kategori_id == kategori_id)
    if cari is not None:
        pernyataan = pernyataan.where(col(Tugas.judul).contains(cari))
    return session.exec(pernyataan.offset(offset).limit(limit)).all()


@router.get("/{tugas_id}", response_model=TugasDenganKategori)
def ambil_tugas(tugas: TugasDiakses):
    return tugas


@router.put("/{tugas_id}", response_model=TugasPublik)
def ganti_tugas(data: TugasBuat, tugas: TugasDiakses, session: SessionDep):
    pastikan_kategori_ada(session, data.kategori_id)
    pastikan_judul_unik(session, tugas.pemilik_id, data.judul, abaikan_id=tugas.id)
    tugas.sqlmodel_update(data.model_dump())
    session.add(tugas)
    session.commit()
    session.refresh(tugas)
    return tugas


@router.patch("/{tugas_id}", response_model=TugasPublik)
def ubah_tugas(data: TugasUbah, tugas: TugasDiakses, session: SessionDep):
    perubahan = data.model_dump(exclude_unset=True)
    for nama in ("judul", "prioritas", "selesai"):
        if nama in perubahan and perubahan[nama] is None:
            raise HTTPException(status_code=400, detail=f"Field '{nama}' tidak boleh null")
    if "judul" in perubahan:
        pastikan_judul_unik(session, tugas.pemilik_id, perubahan["judul"], abaikan_id=tugas.id)
    if "kategori_id" in perubahan:
        pastikan_kategori_ada(session, perubahan["kategori_id"])
    tugas.sqlmodel_update(perubahan)
    session.add(tugas)
    session.commit()
    session.refresh(tugas)
    return tugas


@router.delete("/{tugas_id}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_tugas(tugas: TugasDiakses, session: SessionDep):
    session.delete(tugas)
    session.commit()
