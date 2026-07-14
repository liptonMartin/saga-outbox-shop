import json

import asyncpg

from common.repository import BaseRepository
from services.user_service.models import UserFullInfo
from common.models import User


class UserRepository(BaseRepository):
    async def get_user(self, user_id: str | None, username: str | None) -> User | None:
        if not user_id and not username:
            raise RuntimeError("Failed to get user, because nothing user_id and username is None")

        if user_id:
            user = await self.get_user_by_id(user_id)
            return User(**user.model_dump()) if user else None
        user = await self.get_user_by_username(username)  # pyrefly: ignore [bad-argument-type]
        return User(**user.model_dump()) if user else None

    async def get_user_by_id(self, user_id: str) -> UserFullInfo | None:
        query = self.__create_query_select_user_by_id()
        record = await self.fetchrow(query, user_id)
        if not record:
            return None

        return self.__create_user_full_info(record)

    async def get_user_by_username(self, username: str) -> UserFullInfo | None:
        query = self.__create_query_select_user_by_username()
        record = await self.fetchrow(query, username)
        if not record:
            return None

        return self.__create_user_full_info(record)

    async def update_refresh_token(self, user_id: str, token: str) -> None:
        query = self.__create_query_update_refresh_token()
        await self.execute(query, token, user_id)

    async def create_user(self, user_id: str, username: str, password: str) -> None:
        query = self.__create_query_insert_user()
        await self.execute(query, user_id, username, password)

    async def list_users(self, limit: int = 100) -> list[User]:
        query = self.__create_query_select_all_users()
        records = await self.fetch(query, limit)
        return [self.__create_user_from_record(record) for record in records]

    @staticmethod
    def __create_user_from_record(record: asyncpg.Record) -> User:
        return User(id=record["id"], username=record["username"], permissions=record["permissions"] or [])

    @staticmethod
    def __create_user_full_info(record: asyncpg.Record) -> UserFullInfo:
        user = UserRepository.__create_user_from_record(record)
        return UserFullInfo(
            **user.model_dump(),
            hash_password=record["password"],
            hash_refresh_token=record.get("refresh_token", None)
        )

    @staticmethod
    def __create_query_select_all_users() -> str:
        return "SELECT * FROM users LIMIT $1;"

    @staticmethod
    def __create_query_select_user_by_id() -> str:
        return "SELECT * FROM users WHERE id = $1"

    @staticmethod
    def __create_query_select_user_by_username() -> str:
        return "SELECT * FROM users WHERE username = $1"

    @staticmethod
    def __create_query_insert_user() -> str:
        return "INSERT INTO users (id, username, password) VALUES ($1, $2, $3)"

    @staticmethod
    def __create_query_update_refresh_token() -> str:
        return "UPDATE users SET refresh_token = $1 WHERE id = $2"
