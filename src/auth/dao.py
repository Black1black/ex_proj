from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError

from src.auth.models import AuthToken
from src.dao.base import BaseDAO
from src.databases.postgres import async_session_maker
from src.logger import logger


class AuthDAO(BaseDAO):
    model = AuthToken

    @classmethod
    async def add_token(cls, user_id, token):
        "Добавляем рефреш токен в базу"
        # TODO - пример логирования
        try:
            async with async_session_maker() as session:
                query = insert(cls.model).values(user_id=user_id, token=token)
                await session.execute(query)
                await session.commit()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                message = 'Postgres Exception'
            else:
                message = 'Unknown Exception'
            extra = {
                'user_id': user_id,
                'token': token
            }

            logger.error(
                f'{message}: Cannot add refresh token',
                extra=extra,
                exc_info=True # Прокинем саму ошибку в логи (Но если слишком длинный текст - неудобно будет читать)
            )

