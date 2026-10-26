import warnings

import pytest
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict

from config import KUNCI_CONTOH, Settings

KUNCI = "k" * 40


@pytest.fixture(autouse=True)
def lingkungan_bersih(monkeypatch, tmp_path):
    """Setiap pengujian mulai tanpa variabel TUGASKU_ dari mesin dan di folder kosong (tanpa .env)."""
    import os

    for nama in list(os.environ):
        if nama.startswith("TUGASKU_"):
            monkeypatch.delenv(nama)
    monkeypatch.chdir(tmp_path)


def test_rahasia_wajib():
    with pytest.raises(ValidationError) as galat:
        Settings()
    assert "secret_key" in str(galat.value)


def test_lingkungan_hanya_nilai_yang_dikenal(monkeypatch):
    monkeypatch.setenv("TUGASKU_SECRET_KEY", KUNCI)
    monkeypatch.setenv("TUGASKU_LINGKUNGAN", "staging")
    with pytest.raises(ValidationError) as galat:
        Settings()
    assert "lingkungan" in str(galat.value)


def test_nilai_bawaan_pengembangan(monkeypatch):
    monkeypatch.setenv("TUGASKU_SECRET_KEY", KUNCI)
    s = Settings()
    assert s.lingkungan == "pengembangan"
    assert s.mode_debug is False


# --- Aturan khusus produksi -------------------------------------------------------------
def test_produksi_dengan_konfigurasi_aman_diterima(monkeypatch):
    monkeypatch.setenv("TUGASKU_SECRET_KEY", KUNCI)
    monkeypatch.setenv("TUGASKU_LINGKUNGAN", "produksi")
    assert Settings().lingkungan == "produksi"


@pytest.mark.parametrize(
    "nama, nilai, pesan",
    [
        ("TUGASKU_MODE_DEBUG", "true", "mode_debug harus False"),
        ("TUGASKU_ORIGIN_DIIZINKAN", '["*"]', "tidak boleh berisi '*'"),
        ("TUGASKU_SECRET_KEY", KUNCI_CONTOH + "-" + "x" * 20, "masih kunci contoh"),
    ],
)
def test_produksi_menolak_konfigurasi_berbahaya(monkeypatch, nama, nilai, pesan):
    monkeypatch.setenv("TUGASKU_SECRET_KEY", KUNCI)
    monkeypatch.setenv("TUGASKU_LINGKUNGAN", "produksi")
    monkeypatch.setenv(nama, nilai)
    with pytest.raises(ValidationError) as galat:
        Settings()
    assert pesan in str(galat.value)


def test_hal_yang_sama_boleh_di_pengembangan(monkeypatch):
    monkeypatch.setenv("TUGASKU_SECRET_KEY", KUNCI_CONTOH + "-" + "x" * 20)
    monkeypatch.setenv("TUGASKU_MODE_DEBUG", "true")
    monkeypatch.setenv("TUGASKU_ORIGIN_DIIZINKAN", '["*"]')
    s = Settings()  # tidak ada galat: lingkungan pengembangan
    assert s.mode_debug is True


# --- Sumber dan prioritas --------------------------------------------------------------------
def test_berkas_env_dibaca(tmp_path):
    (tmp_path / ".env").write_text(f"TUGASKU_SECRET_KEY={KUNCI}\nTUGASKU_LINGKUNGAN=uji\n", encoding="utf-8")
    assert Settings().lingkungan == "uji"


def test_env_lokal_menimpa_env(tmp_path):
    (tmp_path / ".env").write_text(f"TUGASKU_SECRET_KEY={KUNCI}\nTUGASKU_LINGKUNGAN=uji\n", encoding="utf-8")
    (tmp_path / ".env.lokal").write_text("TUGASKU_LINGKUNGAN=pengembangan\n", encoding="utf-8")
    assert Settings().lingkungan == "pengembangan"


def test_variabel_environment_menang_atas_berkas_env(monkeypatch, tmp_path):
    (tmp_path / ".env").write_text(f"TUGASKU_SECRET_KEY={KUNCI}\nTUGASKU_LINGKUNGAN=uji\n", encoding="utf-8")
    monkeypatch.setenv("TUGASKU_LINGKUNGAN", "pengembangan")
    assert Settings().lingkungan == "pengembangan"


def test_berkas_rahasia_dibaca(tmp_path):
    folder = tmp_path / "rahasia"
    folder.mkdir()
    (folder / "tugasku_secret_key").write_text(KUNCI, encoding="utf-8")  # nama berkas = awalan + nama field
    s = Settings(_secrets_dir=str(folder))
    assert s.secret_key.get_secret_value() == KUNCI


def test_environment_menang_atas_berkas_rahasia(monkeypatch, tmp_path):
    folder = tmp_path / "rahasia"
    folder.mkdir()
    (folder / "tugasku_secret_key").write_text("a" * 40, encoding="utf-8")
    monkeypatch.setenv("TUGASKU_SECRET_KEY", "b" * 40)
    assert Settings(_secrets_dir=str(folder)).secret_key.get_secret_value() == "b" * 40


def test_folder_rahasia_yang_tidak_ada_hanya_memberi_peringatan(monkeypatch, tmp_path):
    monkeypatch.setenv("TUGASKU_SECRET_KEY", KUNCI)
    with warnings.catch_warnings(record=True) as peringatan:
        warnings.simplefilter("always")
        Settings(_secrets_dir=str(tmp_path / "tidak-ada"))
    assert len(peringatan) >= 1


class SettingsKetat(Settings):
    """Pengaturan bawaan pydantic-settings: entri tak dikenal di .env ditolak."""

    model_config = SettingsConfigDict(
        env_prefix="TUGASKU_", env_file=(".env", ".env.lokal"), extra="forbid"
    )


def test_entri_lain_di_env_diabaikan(tmp_path):
    (tmp_path / ".env").write_text(f"TUGASKU_SECRET_KEY={KUNCI}\nCOMPOSE_PROJECT_NAME=lain\n", encoding="utf-8")
    Settings()  # tidak ada galat


def test_entri_lain_di_env_ditolak_pada_pengaturan_ketat(tmp_path):
    (tmp_path / ".env").write_text(f"TUGASKU_SECRET_KEY={KUNCI}\nCOMPOSE_PROJECT_NAME=lain\n", encoding="utf-8")
    with pytest.raises(ValidationError) as galat:
        SettingsKetat()
    assert "extra_forbidden" in str(galat.value)
    assert "compose_project_name" in str(galat.value)


def test_salah_ketik_nama_variabel_tidak_ketahuan_bila_diabaikan(tmp_path):
    # Risiko extra="ignore": TUGASKU_LINGKUNAN (salah ketik) diabaikan dan lingkungan tetap bawaan
    (tmp_path / ".env").write_text(f"TUGASKU_SECRET_KEY={KUNCI}\nTUGASKU_LINGKUNAN=produksi\n", encoding="utf-8")
    assert Settings().lingkungan == "pengembangan"
    with pytest.raises(ValidationError):
        SettingsKetat()  # pengaturan ketat menangkap salah ketik itu
