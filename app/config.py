from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application configuration settings using Pydantic Settings."""

    # Application
    app_name: str = Field(default="URL Shortener API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    base_url: str = Field(default="http://localhost:8000", description="Base URL for shortened links")

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./url_shortener.db",
        description="Database connection URL"
    )
    database_echo: bool = Field(default=False, description="Echo SQL queries")

    # URL Shortening
    short_code_length: int = Field(default=7, ge=4, le=20, description="Length of generated short codes")
    max_url_length: int = Field(default=2048, description="Maximum URL length")
    allow_custom_codes: bool = Field(default=True, description="Allow custom short codes")
    custom_code_min_length: int = Field(default=3, description="Minimum custom code length")
    custom_code_max_length: int = Field(default=20, description="Maximum custom code length")
    max_collision_retries: int = Field(default=5, description="Maximum retries for collision handling")

    # CORS
    cors_origins: List[str] = Field(default=["*"], description="Allowed CORS origins")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
