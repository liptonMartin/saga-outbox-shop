from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from pwdlib import PasswordHash

from common.utils import create_lifespan
from services.user_service.models import AppConfig, PostgresConfig
from services.user_service.repository.user_repository import UserRepository
from services.user_service.routers.auth import router


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncGenerator[None, None]:
    base_lifespan = create_lifespan(UserRepository, PostgresConfig, AppConfig)

    password_hash = PasswordHash.recommended()

    fastapi_app.state.password_hash = password_hash

    async with base_lifespan(fastapi_app):
        yield


app = FastAPI(lifespan=lifespan)

app.include_router(router)
