from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Dibaca dari variabel environment berawalan TUGASKU_ atau dari berkas .env
    model_config = SettingsConfigDict(env_prefix="TUGASKU_", env_file=".env")

    nama_aplikasi: str = "TugasKu API"
    database_url: str = "sqlite:///database.db"
    algoritma: str = "HS256"
    detik_akses: int = Field(default=1800, ge=60)
    origin_diizinkan: list[str] = ["http://localhost:3000"]
    secret_key: SecretStr = Field(min_length=32)  # wajib diisi


@lru_cache
def get_settings() -> Settings:
    return Settings()
