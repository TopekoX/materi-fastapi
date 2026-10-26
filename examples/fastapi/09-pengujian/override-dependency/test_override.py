from main import PengirimEmail, Settings, app, get_pengirim, get_settings, pengguna_saat_ini


# --- 1. Mengganti konfigurasi --------------------------------------------------------
def test_info_memakai_konfigurasi_bawaan(client):
    response = client.get("/info")
    assert response.json() == {"nama_aplikasi": "TugasKu", "batas_tugas": 100}


def test_info_dengan_konfigurasi_pengganti(client):
    def settings_uji():
        return Settings(nama_aplikasi="TugasKu (uji)", batas_tugas=2)

    app.dependency_overrides[get_settings] = settings_uji
    response = client.get("/info")
    assert response.json() == {"nama_aplikasi": "TugasKu (uji)", "batas_tugas": 2}


# --- 2. Mengganti autentikasi ---------------------------------------------------------
def test_tanpa_override_butuh_header(client):
    assert client.get("/saya").status_code == 422
    assert client.get("/saya", headers={"X-Pengguna": "hantu"}).status_code == 401


def test_autentikasi_diganti_pengguna_tetap(client):
    app.dependency_overrides[pengguna_saat_ini] = lambda: "pengguna-uji"
    response = client.get("/saya")  # tanpa header sama sekali
    assert response.status_code == 200
    assert response.json() == {"pengguna": "pengguna-uji"}


# --- 3. Mengganti layanan luar dengan pengganti palsu (fake) ---------------------------------
class PengirimPalsu(PengirimEmail):
    def __init__(self):
        self.terkirim: list[tuple[str, str]] = []

    def kirim(self, tujuan: str, isi: str) -> None:
        self.terkirim.append((tujuan, isi))


def test_buat_tugas_tanpa_override_gagal_karena_email(client):
    response = client.post("/tugas", json={"judul": "Belajar override"}, headers={"X-Pengguna": "budi"})
    assert response.status_code == 500  # PengirimEmail asli melempar RuntimeError


def test_buat_tugas_dengan_pengirim_palsu(client):
    pengirim = PengirimPalsu()
    app.dependency_overrides[get_pengirim] = lambda: pengirim
    response = client.post("/tugas", json={"judul": "Belajar override"}, headers={"X-Pengguna": "budi"})
    assert response.status_code == 201
    assert pengirim.terkirim == [("budi@contoh.id", "Tugas 'Belajar override' dibuat")]


# --- 4. Beberapa override sekaligus ----------------------------------------------------------
def test_batas_tugas_tercapai(client):
    app.dependency_overrides[get_settings] = lambda: Settings(batas_tugas=1)
    app.dependency_overrides[get_pengirim] = lambda: PengirimPalsu()
    app.dependency_overrides[pengguna_saat_ini] = lambda: "pengguna-uji"
    pertama = client.post("/tugas", json={"judul": "Tugas pertama"})
    kedua = client.post("/tugas", json={"judul": "Tugas kedua"})
    assert pertama.status_code == 201
    assert kedua.status_code == 409
    assert kedua.json() == {"detail": "Batas jumlah tugas tercapai"}


# --- 5. Override tidak bocor ke pengujian lain (berkat fixture bersihkan) -------------------------
def test_override_sudah_dilepas(client):
    assert app.dependency_overrides == {}
    response = client.get("/info")
    assert response.json()["batas_tugas"] == 100
