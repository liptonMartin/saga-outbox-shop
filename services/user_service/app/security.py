from pwdlib import PasswordHash

from common.models import User
from services.user_service.repository.user_repository import UserRepository


async def authenticate_user(
    repository: UserRepository,
    password_hash: PasswordHash,
    dummy_hash: str,
    username: str,
    password: str,
) -> User | None:
    user = await repository.get_user_by_username(username)
    if not user:
        password_hash.verify(password, dummy_hash)
        return None
    return user
