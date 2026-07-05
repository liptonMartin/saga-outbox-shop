from typing import Annotated

import jwt
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from common.models import BaseAppConfig, User
from common.repository import BaseRepository


def get_repository(request: Request) -> BaseRepository:
    return request.state.repository


def get_app_config(request: Request) -> BaseAppConfig:
    return request.state.app_config


def get_oauth2_scheme(request: Request) -> OAuth2PasswordBearer:
    return request.state.oauth2_scheme


def get_user_from_token(access_token: Annotated[str, Depends(get_oauth2_scheme)], config: BaseAppConfig) -> User:
    try:
        payload = jwt.decode(access_token, config.public_key, algorithms=[config.algorithm])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return User(id=payload["sub"], **payload)

