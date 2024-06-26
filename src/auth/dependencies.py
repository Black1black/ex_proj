# Заисимости для проверки, аутонтифицирован ли пользователь
from datetime import datetime

from fastapi import (  # Неопходимо чтобы распарсить информацию о токенах из запроса
    Depends,
    Request,
)
from jose import JWTError, jwt

from src.auth.constants import access_token_name, refresh_token_name
from src.auth.dao import AuthDAO
from src.config import settings
from src.exceptions import (  # TODO кастомные ошибки
    IncorrectTokenFormatException,
    TokenAbsentException,
    TokenExpiredException,
    UserIsNotPresentException,
)
from src.users.dao import UsersDAO
from src.users.models import Users


class TokenDependency:
    def __init__(self, token_name: str):
        self.token_name = token_name

    def get_token(self, request: Request):
        "Забираем токен из cookies"
        token = request.cookies.get(self.token_name)

        # далее адаптация под React Native где нет cookies
        if not request.cookies:
            if self.token_name == refresh_token_name:
                token = request.headers.get("X-Refresh-Token", None)
                # TODO - вынести заголовки в константы
            elif self.token_name == access_token_name:
                request_result = request.headers.get("Authorization", None)
                if request_result:
                    auth_type, auth_info = request.headers.get("Authorization", None).split()
                    if auth_type.lower() == "bearer":
                        token = auth_info

        if not token:
            raise TokenAbsentException
        return token

    def __call__(self):
        return self.get_token


def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        return payload

    except JWTError:
        raise IncorrectTokenFormatException  # TODO Некорректный формат токена


async def get_user_refresh_token(token: str = Depends(TokenDependency(refresh_token_name)())):

    payload = decode_token(token)

    expire: str = payload.get("exp")  # Получаем дату истечения
    if (not expire) or (int(expire) < datetime.utcnow().timestamp()):
        TokenExpiredException  # # TODO Токен истёк

    user_id: str = payload.get("sub")  # Получаем id пользователя
    if not user_id:
        raise UserIsNotPresentException  # Без комментариев, в целях безопасности>

    user = await UsersDAO.find_one_or_none(id=int(user_id))  # Используем функцию для поиска юзера

    if not user:
        raise UserIsNotPresentException  # Без комментариев, в целях безопасности>

    # TODO Добавить блок проверки токена в бд, если его нет - удалять из кук
    validate = await AuthDAO.find_one_or_none(user_id=user.id, token=token)
    if not validate:
        raise IncorrectTokenFormatException

    return token  # TODO - прописать аналогичный метод под токен


async def get_current_user(token: str = Depends(TokenDependency(access_token_name)())):
    "Проверка access токена"
    payload = decode_token(token)

    expire: str = payload.get("exp")
    if (not expire) or (int(expire) < datetime.utcnow().timestamp()):
        TokenExpiredException  # Токен истёк

    user_id: str = payload.get("sub")
    if not user_id:
        raise UserIsNotPresentException
        # Без комментариев, в целях безопасности>

    user = await UsersDAO.find_me(id=int(user_id))

    if not user:
        raise UserIsNotPresentException  # Без комментариев, в целях безопасности>

    return user  # TODO Лучше создать отдельно метод чтобы возвращать без пароля // привести к схеме
