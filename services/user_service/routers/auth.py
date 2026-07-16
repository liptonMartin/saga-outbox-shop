from common.models import Role
from fastapi import Body
from common.utils import check_permission
import secrets
from datetime import datetime
from typing import Annotated
from uuid import uuid4

import jwt
from fastapi import APIRouter, HTTPException, status, Cookie
from fastapi.responses import JSONResponse
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from pwdlib import PasswordHash

from common.dependencies import get_repository, get_app_config, get_user_from_token
from services.user_service.app.dependencies import get_password_hash
from services.user_service.app.security import authenticate_user
from services.user_service.models import Token, AppConfig, TokenType
from common.models import User, Permission
from services.user_service.repository.user_repository import UserRepository

router = APIRouter(prefix="/api/v1/users")


@router.post("/register")
async def post_register(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    repository: Annotated[UserRepository, Depends(get_repository)],
    password_hash: Annotated[PasswordHash, Depends(get_password_hash)],
) -> User:
    hashed_password = password_hash.hash(form_data.password)
    uuid = str(uuid4())
    await repository.create_user(uuid, form_data.username, hashed_password)
    return User(id=uuid, username=form_data.username)


@router.post("/access_token")
async def post_access_token(
    repository: Annotated[UserRepository, Depends(get_repository)],
    app_config: Annotated[AppConfig, Depends(get_app_config)],
    password_hash: Annotated[PasswordHash, Depends(get_password_hash)],
    refresh_token: str = Cookie(),
) -> Token:
    try:
        payload = jwt.decode(refresh_token, app_config.public_key, algorithms=[app_config.algorithm])
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if payload["token_type"] != TokenType.REFRESH_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    user = await repository.get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    dummy_hash = app_config.dummy_hash or password_hash.hash(secrets.token_urlsafe(32))
    if not password_hash.verify(refresh_token, user.hash_refresh_token or dummy_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    exp = datetime.now() + app_config.access_token_duration
    payload = {
        "sub": user.id,
        "iss": "user_service",
        "exp": exp,
        "token_type": TokenType.ACCESS_TOKEN,
        "username": user.username,
        "scopes": user.roles
    }
    token = jwt.encode(payload, app_config.private_key, algorithm=app_config.algorithm)

    return Token(token=token, token_type=TokenType.ACCESS_TOKEN)


@router.post("/refresh_token")
async def post_refresh_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    repository: Annotated[UserRepository, Depends(get_repository)],
    app_config: Annotated[AppConfig, Depends(get_app_config)],
    password_hash: Annotated[PasswordHash, Depends(get_password_hash)],
) -> JSONResponse:
    dummy_hash = app_config.dummy_hash or password_hash.hash(secrets.token_urlsafe(32))
    user = await authenticate_user(repository, password_hash, dummy_hash, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    exp = datetime.now() + app_config.refresh_token_duration
    payload = {"sub": user.id, "iss": "user_service", "exp": exp, "token_type": TokenType.REFRESH_TOKEN}
    token = jwt.encode(payload, app_config.private_key, algorithm=app_config.algorithm)

    response = JSONResponse(content={"message": "successfully created"}, status_code=status.HTTP_201_CREATED)

    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        secure=False,  # TODO: only for development
        samesite="lax",
    )

    hashed_token = password_hash.hash(token)
    await repository.update_refresh_token(user.id, hashed_token)

    return response


@router.get("/list")
async def get_list_users(
    user: Annotated[User, Depends(get_user_from_token)],
    repository: Annotated[UserRepository, Depends(get_repository)],
) -> list[User]:
    check_permission(user, Permission.VIEW_USERS)
    users = await repository.list_users()
    return users


@router.get("/{user_id}")
async def get_user(
    user_id: str,
    current_user: Annotated[User, Depends(get_user_from_token)],
    repository: Annotated[UserRepository, Depends(get_repository)]
) -> User:
    check_permission(current_user, Permission.VIEW_USERS)

    user = await repository.get_user(user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/edit_roles")
async def edit_roles(
    current_user: Annotated[User, Depends(get_user_from_token)],
    repository: Annotated[UserRepository, Depends(get_repository)],
    roles: Annotated[list[Role], Body()],
    user_id: Annotated[str, Body()],
) -> User:
    check_permission(current_user, Permission.CHANGE_ROLES)

    user = await repository.get_user(user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    existed_roles = user.roles
    roles = list(set(roles) | set(existed_roles))
    await repository.update_user_roles(user_id, roles)
    user.roles = roles
    return user
