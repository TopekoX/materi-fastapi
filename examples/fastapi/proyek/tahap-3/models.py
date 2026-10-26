from sqlmodel import Field, Relationship, SQLModel


# --- Kategori ---------------------------------------------------------
class KategoriDasar(SQLModel):
    nama: str = Field(min_length=2, max_length=50)


class Kategori(KategoriDasar, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tugas: list["Tugas"] = Relationship(back_populates="kategori")


class KategoriBuat(KategoriDasar):
    pass


class KategoriPublik(KategoriDasar):
    id: int


# --- Tugas ------------------------------------------------------------
class TugasDasar(SQLModel):
    judul: str = Field(min_length=3, max_length=100)
    catatan: str | None = Field(default=None, max_length=500)
    prioritas: int = Field(default=2, ge=1, le=3, description="1 = tinggi, 3 = rendah")
    selesai: bool = False
    kategori_id: int | None = Field(default=None, foreign_key="kategori.id")


class Tugas(TugasDasar, table=True):
    id: int | None = Field(default=None, primary_key=True)
    kategori: Kategori | None = Relationship(back_populates="tugas")


class TugasBuat(TugasDasar):
    pass


class TugasUbah(SQLModel):
    judul: str | None = Field(default=None, min_length=3, max_length=100)
    catatan: str | None = Field(default=None, max_length=500)
    prioritas: int | None = Field(default=None, ge=1, le=3)
    selesai: bool | None = None
    kategori_id: int | None = None


class TugasPublik(TugasDasar):
    id: int


class TugasDenganKategori(TugasPublik):
    kategori: KategoriPublik | None = None
