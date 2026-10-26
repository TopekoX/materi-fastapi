import httpx


def ambil_kurs() -> float:
    """Mengambil kurs dari layanan luar. Alamatnya sengaja tidak ada (.invalid), jadi selalu gagal."""
    respons = httpx.get("https://api.kurs-contoh.invalid/kurs", timeout=2)
    respons.raise_for_status()
    return respons.json()["kurs"]
