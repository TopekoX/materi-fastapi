from pydantic import ValidationError

from models import Pengguna

# 1. Membuat objek model dari argumen
budi = Pengguna(nama="Budi", umur=25)
print(budi)
print(budi.nama, budi.umur, budi.aktif)

# 2. Mengubah model menjadi dict
print(budi.model_dump())

# 3. Membuat model dari dict, termasuk model bersarang
data = {"nama": "Sari", "umur": 30, "alamat": {"kota": "Makassar"}}
sari = Pengguna.model_validate(data)
print(sari.alamat.kota)

# 4. Konversi tipe otomatis
rina = Pengguna(nama="Rina", umur="28")
print(repr(rina.umur), type(rina.umur).__name__)

# 5. Data tidak valid menghasilkan ValidationError
try:
    Pengguna(nama="Dedi", umur="tiga")
except ValidationError as galat:
    for e in galat.errors():
        print(e["loc"], e["type"], e["msg"])
