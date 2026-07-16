from common.consts import ROLES_PERMISSIONS
import itertools
from fastapi.security import OAuth2PasswordBearer

from common.models import BaseAppConfig, User, Permission
from contextlib import _AsyncGeneratorContextManager
from common.repository import BaseDatabaseConfig
from typing import Any, Callable
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException, status
from contextlib import asynccontextmanager

from common.repository import BaseRepository


def create_lifespan(
    repository_type: type[BaseRepository],
    repository_config_type: type[BaseDatabaseConfig],
    app_config_type: type[BaseAppConfig],
    fastapi_app: FastAPI,
) -> Callable[[], _AsyncGeneratorContextManager[None, Any]]:
    @asynccontextmanager
    async def lifespan() -> AsyncGenerator[None, Any]:
        app_config = app_config_type()
        oauth2_scheme = OAuth2PasswordBearer(tokenUrl="access_token")
        repository = repository_type(repository_config_type())

        fastapi_app.state.app_config = app_config
        fastapi_app.state.oauth2_scheme = oauth2_scheme
        async with repository.start_pool():
            fastapi_app.state.repository = repository
            yield

    return lifespan


def check_permission(user: User, permission: Permission) -> None:
    nested_permissions = [ROLES_PERMISSIONS[role] for role in user.roles]
    user_permissions = itertools.chain.from_iterable(nested_permissions)
    if permission not in user_permissions:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
