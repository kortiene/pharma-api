# -*- coding: utf-8 -*-

import daiquiri
from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

from pharma import __version__

LOGGER = daiquiri.getLogger(__name__)


load_dotenv()


class Settings(BaseSettings):
    """Settings."""

    app: str = "Pharma Services"
    microservice: str = "pharma"
    environment: str = "dev"
    workers: int = 1
    version: str = __version__
    docs_url: str = "/api/pharma/docs"
    openapi_url: str = "/api/pharma/openapi.json"
    metrics_url: str = "/metrics"
    api_port: int = 9090
    log_level: str = "INFO"
    allow_origins: list[str] = []
    api_default_limit: int = 10
    api_default_offset: int = 0
    debug: bool = False
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]
    mongodb_url: str = Field(..., env="MONGODB_URL")
    mongodb_name: str = "pharma"

    @field_validator("allow_origins")
    @classmethod
    def add_additional_allow_origins(
        cls, value: list[str], info: ValidationInfo
    ):
        """Add additional allow_origins."""
        if info.data.get("environment") == "local":
            return value + ["http://localhost", "http://localhost:4200"]
        return value

    @field_validator("debug")
    @classmethod
    def set_debug(cls, value: bool, info: ValidationInfo):
        """Set debug when local or dev."""
        if info.data.get("environment") in ["local", "dev"]:
            return True
        return value

SETTINGS = Settings()
