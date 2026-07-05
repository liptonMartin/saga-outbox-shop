from uuid import UUID

from common.repository import BaseRepository
from services.user_service.models import UserWithPassword
from common.models import User


class UserRepository(BaseRepository):
    async def get_user_by_id(self, user_id: UUID) -> User | None: ...

    async def get_user_by_username(self, username: str) -> UserWithPassword | None: ...

    async def update_refresh_token(self, user_id: UUID, token: str) -> None: ...

    async def create_user(self, user_id: UUID, username: str, password: str) -> None: ...

    async def list_users(self) -> list[User]: ...

