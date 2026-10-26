from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

KUNCI_CONTOH = "ganti-dengan-kunci-acak"  # awalan pada berkas contoh; tidak boleh dipakai di produksi


class Settings(BaseSettings):
    # Urutan sumber (yang awal menang): argumen, variabel environment, berkas .env, berkas rahasia, nilai bawaan.
    # Dua berkas .env: yang belakang menimpa yang depan.
    # extra="ignore": entri di .env yang tidak cocok dengan field diabaikan (bawaan pydantic-settings:
    # "forbid", yang membuat aplikasi gagal mulai bila .env berisi entri lain, mis. milik Docker Compose).
    model_config = SettingsConfigDict(
        env_prefix="TUGASKU_", env_file=(".env", ".env.lokal"), extra="ignore"
    )

    lingkungan: Literal["pengembangan", "uji", "produksi"] = "pengembangan"
    mode_debug: bool = False
    database_url: str = "sqlite:///database.db"
    origin_diizinkan: list[str] = ["http://localhost:3000"]
    secret_key: SecretStr = Field(min_length=32)

    @model_validator(mode="after")
    def periksa_aturan_produksi(self):
        """Di produksi, tolak konfigurasi yang berbahaya. Aplikasi gagal mulai alih-alih berjalan dengan tidak aman."""
        if self.lingkungan == "produksi":
            masalah = []
            if self.mode_debug:
                masalah.append("mode_debug harus False")
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
