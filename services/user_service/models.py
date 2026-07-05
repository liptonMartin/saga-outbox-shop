import pathlib
from datetime import timedelta
from enum import StrEnum

from pydantic_settings import SettingsConfigDict

from common.models import BaseAppConfig, User
from pydantic import BaseModel, computed_field, SecretStr

from common.repository import create_postgres_config


class AppConfig(BaseAppConfig):
    private_key_file: pathlib.Path
    refresh_token_duration: timedelta = timedelta(days=15)
    access_token_duration: timedelta = timedelta(minutes=15)
    dummy_hash: str | None = None

    @computed_field
    @property
    def private_key(self) -> str:
        with open(self.private_key_file, "rb") as file:
            return file.read().decode("utf-8")

    model_config = SettingsConfigDict(**BaseAppConfig.model_config)
    model_config["env_file"] = "services/user_service/.env"

PostgresConfig = create_postgres_config("user_service")


class TokenType(StrEnum):
    ACCESS_TOKEN = "access"
    REFRESH_TOKEN = "refresh"


class Token(BaseModel):
    token: str
    token_type: TokenType


class UserWithPassword(User):
    password: SecretStr
