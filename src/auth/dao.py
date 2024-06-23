from sqlalchemy import delete, insert, select, update

from src.auth.models import AuthToken
from src.dao.base import BaseDAO
from src.databases.postgres import async_session_maker
from src.users.models import Users, UsersLocation


class AuthDAO(BaseDAO):
    model = AuthToken

    @classmethod
    async def add_token(cls, user_id, token):
        "Добавляем рефреш токен в базу"
        async with async_session_maker() as session:
            query = insert(cls.model).values(user_id=user_id, token=token)
            await session.execute(query)  
            await session.commit()
