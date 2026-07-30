from typing import Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.exceptions import ConfigurationError


class Settings(BaseSettings):
    app_port: int = 8000
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    log_level: str = "INFO" 

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore", 
    )

    def model_post_init(self, __context: Any) -> None:
        """
        Performs post-initialization validation for settings.
        Raises ConfigurationError if critical settings are invalid.
        """
        if not self.secret_key or len(self.secret_key) < 32:
            raise ConfigurationError("SECRET_KEY must be at least 32 characters long for security.")


settings = Settings()