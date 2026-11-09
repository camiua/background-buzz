"""Configuración del proyecto, leída del archivo .env de la raíz (spec §1.9)."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    """Variables de entorno del proyecto. Las rutas relativas parten de backend/."""

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    model_path: Path = Path("models/best.pt")
    confidence_threshold: float = Field(default=0.5, ge=0, le=1)
    sample_fps: float = Field(default=5, gt=0)

    @property
    def model_file(self) -> Path:
        """Ruta absoluta del modelo."""
        if self.model_path.is_absolute():
            return self.model_path
        return BACKEND_DIR / self.model_path


settings = Settings()
