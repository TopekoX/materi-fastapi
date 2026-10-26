from sqlmodel import Field, SQLModel


class Tugas(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    judul: str = Field(min_length=3, max_length=100)
    selesai: bool = False
    catatan: str | None = None
    prioritas: int = 2
