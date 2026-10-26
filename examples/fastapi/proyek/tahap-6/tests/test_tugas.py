import pytest


def buat(client, header, judul="Belajar pengujian", **tambahan):
    return client.post("/tugas", json={"judul": judul, **tambahan}, headers=header)


def test_tugas_butuh_login(client):
    for metode, url in [("get", "/tugas"), ("post", "/tugas"), ("get", "/tugas/1"), ("delete", "/tugas/1")]:
        response = getattr(client, metode)(url)
        assert response.status_code == 401, (metode, url)


def test_buat_tugas(client, header_budi):
    response = buat(client, header_budi)
    assert response.status_code == 201
    isi = response.json()
    assert isi["judul"] == "Belajar pengujian"
    assert isi["selesai"] is False
    assert isi["prioritas"] == 2
    assert isi["pemilik_id"] is not None


def test_buat_tugas_dengan_kategori(client, header_budi, kategori_kuliah):
    response = buat(client, header_budi, kategori_id=kategori_kuliah["id"])
    assert response.status_code == 201
    assert response.json()["kategori_id"] == kategori_kuliah["id"]


def test_buat_tugas_kategori_tidak_ada(client, header_budi):
    response = buat(client, header_budi, kategori_id=99)
    assert response.status_code == 404
    assert response.json()["galat"]["kode"] == "KATEGORI_TIDAK_ADA"


def test_judul_kembar_per_pemilik(client, header_budi, header_sari):
    assert buat(client, header_budi, "Belajar FastAPI").status_code == 201
    kembar = buat(client, header_budi, "belajar fastapi")  # huruf besar-kecil tidak dibedakan
    assert kembar.status_code == 409
    assert kembar.json()["galat"]["kode"] == "JUDUL_SUDAH_ADA"
    # pemilik lain boleh memakai judul yang sama
    assert buat(client, header_sari, "Belajar FastAPI").status_code == 201


@pytest.mark.parametrize(
    "isian, field",
    [
        ({"judul": "ab"}, "body.judul"),
        ({"judul": "Judul sah", "prioritas": 9}, "body.prioritas"),
        ({"judul": "x" * 101}, "body.judul"),
    ],
)
def test_validasi_buat_tugas(client, header_budi, isian, field):
    response = client.post("/tugas", json=isian, headers=header_budi)
    assert response.status_code == 422
    rincian = response.json()["galat"]["rincian"]
    assert field in [r["field"] for r in rincian]


def test_daftar_hanya_milik_sendiri(client, header_budi, header_sari):
    buat(client, header_budi, "Tugas milik Budi")
    buat(client, header_sari, "Tugas milik Sari")
    judul_budi = [t["judul"] for t in client.get("/tugas", headers=header_budi).json()]
    judul_sari = [t["judul"] for t in client.get("/tugas", headers=header_sari).json()]
    assert judul_budi == ["Tugas milik Budi"]
    assert judul_sari == ["Tugas milik Sari"]


def test_filter_dan_paginasi(client, header_budi):
    buat(client, header_budi, "Tugas satu", selesai=True)
    buat(client, header_budi, "Tugas dua")
    buat(client, header_budi, "Cuci motor")
    selesai = client.get("/tugas", params={"selesai": True}, headers=header_budi).json()
    assert [t["judul"] for t in selesai] == ["Tugas satu"]
    cari = client.get("/tugas", params={"cari": "motor"}, headers=header_budi).json()
    assert [t["judul"] for t in cari] == ["Cuci motor"]
    halaman = client.get("/tugas", params={"limit": 1, "offset": 1}, headers=header_budi).json()
    assert [t["judul"] for t in halaman] == ["Tugas dua"]


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}, {"cari": "a"}])
def test_parameter_daftar_tidak_valid(client, header_budi, params):
    response = client.get("/tugas", params=params, headers=header_budi)
    assert response.status_code == 422


def test_ambil_tugas_menyertakan_kategori(client, header_budi, kategori_kuliah):
    dibuat = buat(client, header_budi, kategori_id=kategori_kuliah["id"]).json()
    response = client.get(f"/tugas/{dibuat['id']}", headers=header_budi)
    assert response.status_code == 200
    assert response.json()["kategori"] == kategori_kuliah


def test_ambil_tugas_tidak_ada(client, header_budi):
    response = client.get("/tugas/99", headers=header_budi)
    assert response.status_code == 404
    assert response.json()["galat"]["kode"] == "TUGAS_TIDAK_ADA"


def test_id_tidak_valid(client, header_budi):
    assert client.get("/tugas/0", headers=header_budi).status_code == 422
    assert client.get("/tugas/abc", headers=header_budi).status_code == 422


def test_ganti_tugas_mengembalikan_isian_tak_dikirim_ke_bawaan(client, header_budi):
    dibuat = buat(client, header_budi, catatan="penting", prioritas=1).json()
    response = client.put(f"/tugas/{dibuat['id']}", json={"judul": "Judul baru"}, headers=header_budi)
    assert response.status_code == 200
    isi = response.json()
    assert isi["judul"] == "Judul baru"
    assert isi["catatan"] is None  # PUT mengganti seluruhnya
    assert isi["prioritas"] == 2


def test_ubah_sebagian_hanya_mengubah_yang_dikirim(client, header_budi):
    dibuat = buat(client, header_budi, catatan="penting", prioritas=1).json()
    response = client.patch(f"/tugas/{dibuat['id']}", json={"selesai": True}, headers=header_budi)
    assert response.status_code == 200
    isi = response.json()
    assert isi["selesai"] is True
    assert isi["catatan"] == "penting"  # tidak berubah
    assert isi["prioritas"] == 1


def test_patch_boleh_menghapus_catatan(client, header_budi):
    dibuat = buat(client, header_budi, catatan="penting").json()
    response = client.patch(f"/tugas/{dibuat['id']}", json={"catatan": None}, headers=header_budi)
    assert response.json()["catatan"] is None


@pytest.mark.parametrize("field", ["judul", "prioritas", "selesai"])
def test_patch_menolak_null_untuk_field_wajib(client, header_budi, field):
    dibuat = buat(client, header_budi).json()
    response = client.patch(f"/tugas/{dibuat['id']}", json={field: None}, headers=header_budi)
    assert response.status_code == 400


def test_patch_judul_kembar(client, header_budi):
    buat(client, header_budi, "Judul pertama")
    kedua = buat(client, header_budi, "Judul kedua").json()
    response = client.patch(f"/tugas/{kedua['id']}", json={"judul": "judul pertama"}, headers=header_budi)
    assert response.status_code == 409


def test_patch_boleh_memakai_judul_sendiri(client, header_budi):
    dibuat = buat(client, header_budi, "Judul saya").json()
    response = client.patch(f"/tugas/{dibuat['id']}", json={"judul": "Judul saya"}, headers=header_budi)
    assert response.status_code == 200


def test_hapus_tugas(client, header_budi):
    dibuat = buat(client, header_budi).json()
    assert client.delete(f"/tugas/{dibuat['id']}", headers=header_budi).status_code == 204
    assert client.get(f"/tugas/{dibuat['id']}", headers=header_budi).status_code == 404
    assert client.delete(f"/tugas/{dibuat['id']}", headers=header_budi).status_code == 404


def test_filter_kategori(client, header_budi, kategori_kuliah):
    buat(client, header_budi, "Tugas kuliah", kategori_id=kategori_kuliah["id"])
    buat(client, header_budi, "Tugas tanpa kategori")
    response = client.get("/tugas", params={"kategori_id": kategori_kuliah["id"]}, headers=header_budi)
    assert [t["judul"] for t in response.json()] == ["Tugas kuliah"]


def test_patch_kategori_tidak_ada(client, header_budi):
    dibuat = buat(client, header_budi).json()
    response = client.patch(f"/tugas/{dibuat['id']}", json={"kategori_id": 99}, headers=header_budi)
    assert response.status_code == 404
    assert response.json()["galat"]["kode"] == "KATEGORI_TIDAK_ADA"
