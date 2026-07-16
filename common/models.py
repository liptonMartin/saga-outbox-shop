import pathlib
from enum import StrEnum

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
    VIEW_USERS = "view_users"  # просматривать пользователей
    CHANGE_ROLES = "change_roles"  # менять роли у пользователей


class Role(StrEnum):
    STAFF = "staff"  # возможность работы с пользователями


class User(BaseModel):
    id: str
    username: str
    roles: list[Role] = []
