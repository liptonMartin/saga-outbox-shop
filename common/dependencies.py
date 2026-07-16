from typing import Annotated

import jwt
from fastapi import Request, Depends, HTTPException, status

from common.models import BaseAppConfig, User
from common.repository import BaseRepository


def get_repository(request: Request) -> BaseRepository:
    return request.app.state.repository


def get_app_config(request: Request) -> BaseAppConfig:
    return request.app.state.app_config


async def get_oauth2_scheme(request: Request) -> str:
    return await request.app.state.oauth2_scheme(request)


def get_user_from_token(
    access_token: Annotated[str, Depends(get_oauth2_scheme)],
    config: Annotated[BaseAppConfig, Depends(get_app_config)],
) -> User:
    try:
        payload = jwt.decode(access_token, config.public_key, algorithms=[config.algorithm])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return User(id=payload["sub"], username=payload["username"], roles=payload["scopes"])
