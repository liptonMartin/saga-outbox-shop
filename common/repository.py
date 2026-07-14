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
            database=self.config.db,
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
    async def transaction(
        self, connection: asyncpg.Connection | None = None
    ) -> AsyncGenerator[asyncpg.Connection, None]:
        if connection:
            async with connection.transaction():
                yield connection
                return
        async with self.connection() as connection:
            async with connection.transaction():
                yield connection

    async def execute(self, query: str, *placeholders, connection: asyncpg.Connection | None = None) -> str:
        if connection:
            return await connection.execute(query, *placeholders)

        async with self.transaction() as connection:
            return await connection.execute(query, *placeholders)

    async def fetch(self, query: str, *placeholders, connection: asyncpg.Connection | None = None) -> list[asyncpg.Record]:
        if connection:
            return await connection.fetch(query, *placeholders)

        async with self.connection() as connection:
            return await connection.fetch(query, *placeholders)

    async def fetchrow(self, query: str, *placeholders, connection: asyncpg.Connection | None = None) -> asyncpg.Record | None:
        if connection:
            return await connection.fetchrow(query, *placeholders)

        async with self.connection() as connection:
            return await connection.fetchrow(query, *placeholders)
