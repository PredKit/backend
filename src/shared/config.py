"""
Configuration management using pydantic-settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Database
    db_host: str = ""
    db_port: int = 5432
    db_name: str = ""
    db_user: str = ""
    db_password: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_default=False,
    )

    @property
    def database_url(self) -> str:
        """Async PostgreSQL connection string"""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def sync_database_url(self) -> str:
        """Sync PostgreSQL connection string (for Alembic with psycopg3)"""
        return f"postgresql+psycopg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


# Global settings instance
settings = Settings()
