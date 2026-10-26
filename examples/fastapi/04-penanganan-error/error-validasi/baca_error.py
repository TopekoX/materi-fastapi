import httpx


def ringkas_error(respons: httpx.Response) -> dict[str, str]:
    """Ubah daftar error 422 menjadi {nama_field: pesan}."""
    hasil: dict[str, str] = {}
    for galat in respons.json()["detail"]:
        # loc[0] = asal data ("body", "query", "path", "header"); sisanya = jalur ke field
        jalur = ".".join(str(bagian) for bagian in galat["loc"][1:])
        hasil[f'{galat["loc"][0]}:{jalur}'] = galat["msg"]
    return hasil


respons = httpx.post(
    "http://127.0.0.1:8000/kelas/0/daftar",
    params={"sumber": "x"},
    json={"nama": "Al", "umur": 12, "alamat": {"kota": "Bandung", "kode_pos": "abc"}},
)
print(respons.status_code)
for field, pesan in ringkas_error(respons).items():
    print(f"{field} -> {pesan}")
