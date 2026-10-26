from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Awalan kunci yang biasa dipakai pada contoh; ditolak di produksi
KUNCI_CONTOH = "ganti-dengan-kunci-acak"


class Settings(BaseSettings):
    # Dibaca dari variabel environment berawalan TUGASKU_ atau dari berkas .env.
    # extra="ignore": entri lain di .env (misalnya milik Docker Compose) tidak menggagalkan aplikasi.
    model_config = SettingsConfigDict(env_prefix="TUGASKU_", env_file=".env", extra="ignore")

    nama_aplikasi: str = "TugasKu API"
    lingkungan: Literal["pengembangan", "uji", "produksi"] = "pengembangan"
    database_url: str = "sqlite:///database.db"
    algoritma: str = "HS256"
    detik_akses: int = Field(default=1800, ge=60)
    origin_diizinkan: list[str] = ["http://localhost:3000"]
    secret_key: SecretStr = Field(min_length=32)  # wajib diisi
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["teks", "json"] = "teks"

    @model_validator(mode="after")
    def periksa_aturan_produksi(self) -> "Settings":
        """Tolak konfigurasi berbahaya saat aplikasi mulai, bukan setelah pengguna menemukannya."""
        if self.lingkungan == "produksi":
            masalah = []
            if "*" in self.origin_diizinkan:
                masalah.append("origin_diizinkan tidak boleh berisi '*'")
            if self.secret_key.get_secret_value().startswith(KUNCI_CONTOH):
                masalah.append("secret_key masih kunci contoh")
            if masalah:
                raise ValueError("Konfigurasi produksi tidak aman: " + "; ".join(masalah))
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
