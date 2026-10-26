from typing import Annotated, Literal, get_args, get_type_hints


def sapa(nama: str, umur: int) -> str:
    return f"Halo {nama}, umur {umur}"


def jumlah(angka: list[int]) -> int:
    return sum(angka)


def panggil(nama: str | None = None) -> str:
    return nama if nama is not None else "tamu"


# Type hints TIDAK dipaksakan oleh Python: argumen yang salah tipe tetap jalan.
print(sapa("Budi", "bukan angka"))
print(jumlah([1, 2, 3]))
print(panggil(), panggil("Sari"))

# Type hints tersimpan sebagai data yang bisa dibaca program lain (inilah yang dipakai FastAPI).
print(get_type_hints(sapa))

Pesan = Annotated[str, "metadata apa saja"]
print(get_args(Pesan))

Level = Literal["rendah", "tinggi"]
print(get_args(Level))
