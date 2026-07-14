import pathlib
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from abc import ABC


class BaseAppConfig(ABC, BaseSettings):
    public_key_file: pathlib.Path
    algorithm: str = "RS256"

    @computed_field
    @property
    def public_key(self) -> str:
        with open(self.public_key_file, "rb") as file:
            return file.read().decode("utf-8")

    model_config = SettingsConfigDict(case_sensitive=False, extra="ignore")


class Permission(StrEnum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class User(BaseModel):
    id: str
    username: str
    permissions: list[Permission] = []
