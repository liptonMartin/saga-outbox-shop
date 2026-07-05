from abc import ABC
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

import asyncpg


class BaseDatabaseConfig(ABC, BaseSettings):
    user: str
    password: SecretStr
    db: str
    host: str
    port: int
    max_connection: int = 20


def create_postgres_config(service_name: str) -> type[BaseDatabaseConfig]:
    class PostgresConfig(BaseDatabaseConfig):
        port: int = 5432

        model_config = SettingsConfigDict(
            env_file=f"services/{service_name}/.env", env_prefix="POSTGRES_", case_sensitive=False, extra="ignore"
        )

    return PostgresConfig


class BaseRepository(ABC):
    def __init__(self, config: BaseDatabaseConfig) -> None:
        self.config = config
        self.pool: asyncpg.Pool | None = None

    @asynccontextmanager
    async def start_pool(self, pool: asyncpg.Pool | None = None) -> AsyncGenerator[None, None]:
        self.pool = pool or await asyncpg.create_pool(
            user=self.config.user,
            password=self.config.password.get_secret_value(),
            host=self.config.host,
            port=self.config.port,
            max_size=self.config.max_connection,
        )

        yield

        await self.pool.close()

    @asynccontextmanager
    async def connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        if not self.pool:
            raise RuntimeError("The connection pool is closed")
        async with self.pool.acquire() as connection:
            yield connection

    @asynccontextmanager
    async def transaction(self, connection: asyncpg.Connection | None = None) -> AsyncGenerator[
        asyncpg.Connection, None]:
        if connection:
            async with connection.transaction():
                yield connection
                return
        async with self.connection() as connection:
            async with connection.transaction():
                yield connection

    @staticmethod
    async def execute(connection: asyncpg.Connection, query: str) -> str:
        return await connection.execute(query)

    @staticmethod
    async def fetch(connection: asyncpg.Connection, query: str) -> list[asyncpg.Record]:
        return await connection.fetch(query)

    @staticmethod
    async def fetchrow(connection: asyncpg.Connection, query: str) -> asyncpg.Record | None:
        return await connection.fetchrow(query)
