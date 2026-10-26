from test_tugas import buat


def test_kategori_hanya_pengelola(client, header_budi, header_pengelola):
    anggota = client.post("/kategori", json={"nama": "Kuliah"}, headers=header_budi)
    assert anggota.status_code == 403
    pengelola = client.post("/kategori", json={"nama": "Kuliah"}, headers=header_pengelola)
    assert pengelola.status_code == 201


def test_daftar_kategori_butuh_login_tetapi_untuk_semua_peran(client, header_budi, kategori_kuliah):
    assert client.get("/kategori").status_code == 401
    response = client.get("/kategori", headers=header_budi)
    assert response.status_code == 200
    assert response.json() == [kategori_kuliah]


def test_kategori_nama_terlalu_pendek(client, header_pengelola):
    response = client.post("/kategori", json={"nama": "K"}, headers=header_pengelola)
    assert response.status_code == 422


def test_tugas_milik_orang_lain_ditolak(client, header_budi, header_sari):
    dibuat = buat(client, header_budi).json()
    url = f"/tugas/{dibuat['id']}"
    assert client.get(url, headers=header_sari).status_code == 403
    assert client.put(url, json={"judul": "Diubah sari"}, headers=header_sari).status_code == 403
    assert client.patch(url, json={"selesai": True}, headers=header_sari).status_code == 403
    assert client.delete(url, headers=header_sari).status_code == 403
    # data tidak berubah
    asli = client.get(url, headers=header_budi).json()
    assert asli["judul"] == "Belajar pengujian"
    assert asli["selesai"] is False


def test_pengelola_boleh_mengakses_semua(client, header_budi, header_pengelola):
    dibuat = buat(client, header_budi).json()
    url = f"/tugas/{dibuat['id']}"
    assert client.get(url, headers=header_pengelola).status_code == 200
    assert client.patch(url, json={"selesai": True}, headers=header_pengelola).status_code == 200
    semua = client.get("/tugas", headers=header_pengelola).json()
    assert [t["id"] for t in semua] == [dibuat["id"]]
    assert client.delete(url, headers=header_pengelola).status_code == 204


def test_pemilik_tidak_bisa_ditentukan_klien(client, header_budi, header_sari):
    sari = client.get("/saya", headers=header_sari).json()
    response = client.post(
        "/tugas", json={"judul": "Coba curi", "pemilik_id": sari["id"]}, headers=header_budi
    )
    assert response.status_code == 201
    assert response.json()["pemilik_id"] != sari["id"]  # field pemilik_id dari klien diabaikan
