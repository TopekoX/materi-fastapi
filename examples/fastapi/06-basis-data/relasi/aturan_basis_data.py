"""Menegakkan aturan di tingkat basis data: foreign key, unique, dan index.

Jalankan dari folder ini: python aturan_basis_data.py
Skrip membuat berkas database.db di folder kerja; hapus setelah dicoba.
"""

from sqlalchemy import event, inspect
from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, Session, SQLModel, create_engine

engine = create_engine("sqlite:///database.db")


# SQLite tidak menegakkan foreign key kecuali diminta pada setiap koneksi baru
@event.listens_for(engine, "connect")
def aktifkan_foreign_key(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Kategori(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nama: str = Field(unique=True, index=True)  # tidak boleh kembar, dan dibuatkan indeks


class Tugas(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    judul: str
    kategori_id: int | None = Field(default=None, foreign_key="kategori.id")


SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    session.add(Kategori(nama="Kuliah"))
    session.commit()

percobaan = [
    ("kategori_id=99", Tugas(judul="x", kategori_id=99)),
    ("nama kembar", Kategori(nama="Kuliah")),
]
for nama, objek in percobaan:
    with Session(engine) as session:
        session.add(objek)
        try:
            session.commit()
            print(nama, "-> tersimpan")
        except IntegrityError as galat:
            print(nama, "-> IntegrityError:", str(galat.orig))

with Session(engine) as session:
    session.add(Kategori(nama="Rumah"))
    session.add(Tugas(judul="ok", kategori_id=1))
    session.commit()
    print("data valid -> tersimpan")

print("indeks kategori:", [(i["name"], i["unique"]) for i in inspect(engine).get_indexes("kategori")])
