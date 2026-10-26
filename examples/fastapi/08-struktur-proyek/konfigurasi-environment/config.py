from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Nilai dibaca dari variabel environment berawalan TUGASKU_ (tanpa membedakan huruf besar-kecil),
    # dan dari berkas .env bila ada. Variabel environment menang atas isi .env.
    model_config = SettingsConfigDict(env_prefix="TUGASKU_", env_file=".env")

    nama_aplikasi: str = "TugasKu"
    mode_debug: bool = False
    database_url: str = "sqlite:///database.db"
    detik_akses: int = Field(default=900, ge=60)
    origin_diizinkan: list[str] = ["http://localhost:3000"]

    # Tidak punya nilai bawaan: WAJIB diisi. SecretStr menyembunyikan nilainya saat dicetak.
    secret_key: SecretStr = Field(min_length=32)
