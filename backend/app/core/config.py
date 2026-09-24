from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
DEVELOPMENT_JWT_SECRET = "dev-secret-troque-em-producao-0123456789abcdef"


class Settings(BaseSettings):
    """Configurações carregadas de variáveis de ambiente ou do arquivo .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    project_name: str = "RocketLab API"
    project_version: str = "2026.2"
    environment: str = "local"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite+aiosqlite:///./rocketlab.db"
    backend_cors_origins: list[str] = ["http://localhost:5173"]
    log_level: str = "INFO"
    jwt_secret_key: str = DEVELOPMENT_JWT_SECRET
    jwt_expires_minutes: int = 480
    admin_email: str = "admin@rocketlab.dev"
    admin_name: str = "Administrador"
    admin_password: str = "rocketlab2026"
    seed_data_dir: Path = BACKEND_DIR / "data" / "seed"

    @property
    def sync_database_url(self) -> str:
        return self.database_url.replace("+aiosqlite", "")

    @model_validator(mode="after")
    def require_secret_outside_local(self) -> "Settings":
        if self.environment == "production" and self.jwt_secret_key == DEVELOPMENT_JWT_SECRET:
            raise ValueError("JWT_SECRET_KEY deve ser definido em produção")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
