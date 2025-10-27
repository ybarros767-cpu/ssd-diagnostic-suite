from __future__ import annotations

from typing import List, Optional, Union

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_env: str = Field(default="development", alias="APP_ENV")
    allowed_origins: Union[str, List[str]] = Field(default="*", alias="ALLOWED_ORIGINS")

    # Auth
    enable_auth: bool = Field(default=False, alias="ENABLE_AUTH")
    jwt_secret: str = Field(default="change-me", alias="JWT_SECRET")
    jwt_exp_minutes: int = Field(default=60, alias="JWT_EXP_MINUTES")
    admin_username: str = Field(default="admin", alias="ADMIN_USERNAME")
    admin_password: str = Field(default="admin", alias="ADMIN_PASSWORD")

    # Database
    enable_db: bool = Field(default=False, alias="ENABLE_DB")
    database_url: str = Field(default="sqlite:////app/data/app.db", alias="DATABASE_URL")

    # Observability
    enable_prometheus: bool = Field(default=True, alias="ENABLE_PROMETHEUS")
    prometheus_port: int = Field(default=9090, alias="PROMETHEUS_PORT")

    # AI
    groq_api_key: Optional[str] = Field(default=None, alias="GROQ_API_KEY")
    groq_model: str = Field(default="mixtral-8x7b-32768", alias="GROQ_MODEL")

    def get_allowed_origins(self) -> List[str]:
        value = self.allowed_origins
        if isinstance(value, list):
            return value or ["*"]
        if not value:
            return ["*"]
        text = value.strip()
        if text == "*":
            return ["*"]
        return [o.strip() for o in text.split(",") if o.strip()]


settings = Settings()
