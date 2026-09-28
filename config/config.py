"""Environment-driven application configuration.

Every setting is read from the environment (or `.env`) through Pydantic Settings,
so a missing or malformed value fails at import time instead of at first request.
The `DB_*` credentials are required; the pool and API knobs have safe defaults.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class CommonSettings(BaseSettings):
    """Application settings resolved from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    db_host: str = Field(..., alias="DB_HOST", min_length=1)
    db_port: int = Field(..., alias="DB_PORT", ge=1, le=65535)
    db_user: str = Field(..., alias="DB_USER", min_length=1)
    db_password: str = Field(..., alias="DB_PASSWORD")
    db_name: str = Field(..., alias="DB_NAME", min_length=1)
    db_echo: bool = Field(False, alias="SQLALCHEMY_ECHO")

    db_pool_size: int = Field(10, alias="DB_POOL_SIZE", ge=1, le=100)
    db_max_overflow: int = Field(20, alias="DB_MAX_OVERFLOW", ge=0, le=200)
    db_pool_recycle: int = Field(1800, alias="DB_POOL_RECYCLE", ge=0)
    db_pool_timeout: int = Field(30, alias="DB_POOL_TIMEOUT", ge=1)

    api_title: str = Field("Products API", alias="API_TITLE")
    api_version: str = Field("1.0.0", alias="API_VERSION")
    gzip_minimum_size: int = Field(500, alias="GZIP_MINIMUM_SIZE", ge=0)

    @property
    def database_url(self) -> URL:
        """Build the SQLAlchemy URL, escaping credentials that contain `@` or `/`."""
        return URL.create(
            drivername="mysql+pymysql",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            query={"charset": "utf8mb4"},
        )
