from contextlib import _AsyncGeneratorContextManager
from common.repository.base_repository import BaseDatabaseConfig
from typing import Any, Callable
from typing import AsyncGenerator
from fastapi import FastAPI
from contextlib import asynccontextmanager

from common.repository.base_repository import BaseRepository


def create_lifespan(
        repository_type: type[BaseRepository], config_type: type[BaseDatabaseConfig]
) -> Callable[[FastAPI], _AsyncGeneratorContextManager[None, Any]]:
    @asynccontextmanager
    async def lifespan(fastapi_app: FastAPI) -> AsyncGenerator[None, Any]:
        repository = repository_type(config_type())
        async with repository.start_pool():
            fastapi_app.state.repository = repository
        yield

    return lifespan
