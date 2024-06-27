from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Response
from jose import jwt

from src.auth.auth import (
    authentificate_user,
    create_jwt_token,
    get_password_hash,
    replace_old_password,
)
from src.auth.constants import access_token_name, refresh_token_name
from src.auth.dao import AuthDAO
from src.auth.dependencies import get_current_user, get_user_refresh_token
from src.auth.schemas import STokens
from src.config import settings
from src.exceptions import IncorrectEmailOrPasswordException, UserAlreadyExistsException
from src.users.dao import UsersDAO
from src.users.models import Users
from src.users.schemas import SUsersAuth, SUsersReg

router = APIRouter(prefix="/auth", tags=["Аутентификация и авторизация"])


@router.post("/registration")
async def registration_user(user_data: SUsersReg):

    existing_user_mail = await UsersDAO.find_one_or_none(email=user_data.email)

    if existing_user_mail:
        raise UserAlreadyExistsException
    hashed_password = get_password_hash(user_data.password)
    await UsersDAO.add_user(
        email=user_data.email.lower(), hashed_password=hashed_password, name=user_data.name
    )

    return {"message": "success"}


@router.post("/login")
async def login(response: Response, user_data: SUsersAuth):

    user = await authentificate_user(user_data.email.lower(), user_data.password)
    if not user:
        raise IncorrectEmailOrPasswordException

    access_token_jwt = create_jwt_token({"sub": str(user.id)})
    refresh_token_jwt = create_jwt_token({"sub": str(user.id)}, is_access=False)

    await AuthDAO.add_token(user_id=user.id, token=refresh_token_jwt)

    # Сетим в cookies если используем веб приложение
    response.set_cookie(access_token_name, access_token_jwt, httponly=True, secure=True)
    response.set_cookie(refresh_token_name, refresh_token_jwt, httponly=True, secure=True)

    tokens_dict = {"access_token": access_token_jwt, "refresh_token": refresh_token_jwt}

    # Отдаём словарь для мобильного приложения через Pydantic в camelCase
    return STokens(**tokens_dict)


@router.post("/refresh")
async def refresh_access_token(
    response: Response, refresh_token: str = Depends(get_user_refresh_token)
):
    # TODO добавить взаимодействие с рефреш токеном

    payload = jwt.decode(
        refresh_token, settings.SECRET_KEY, algorithms=settings.ALGORITHM
    )  # декодируем refresh_token
    user_id = payload.get("sub")
    expire = payload.get("exp")
    # if not user_id or not expire: # Проверяем токен
    #     raise HTTPException(status_code=401, detail="Invalid refresh token") # Уже проверили всё в функции зависимости

    # create new access token
    access_token_jwt = create_jwt_token(data={"sub": str(user_id)})
    response.set_cookie(access_token_name, access_token_jwt, httponly=True, secure=True)

    new_refresh_token = None
    # Если наш рефреш токен подходит к концу - создаём новый
    if (int(expire) - datetime.utcnow().timestamp()) < timedelta(days=5).total_seconds():

        new_refresh_token = create_jwt_token({"sub": str(user_id)}, is_access=False)
        await AuthDAO.add_token(
            user_id=user_id, token=new_refresh_token
        )  # Сохраняем в базе новый токен
        await AuthDAO.delete(token=refresh_token)
        # TODO Создать отдельный DAO поинт, который в рамках одной транзакции запишет новый токен и удалит старый

        response.set_cookie(refresh_token_name, new_refresh_token, httponly=True, secure=True)

    tokens_dict = {"access_token": access_token_jwt, "refresh_token": new_refresh_token}
    print(tokens_dict)
    # Отдаём словарь для мобильного приложения через Pydantic в camelCase
    return STokens(**tokens_dict)


@router.delete("/logout")
async def logout_user(response: Response, refresh_token: str = Depends(get_user_refresh_token)):
    """
    На данном этапе реализована простая система.
    В дальнейшем стоит добавить занесение токенов в чс, а не удаление
    """
    response.delete_cookie(refresh_token_name)
    response.delete_cookie(access_token_name)

    await AuthDAO.delete(token=refresh_token)

    return {"message": "success"}


@router.patch("/replace_password", name="Замена пароля пользователя")  #
async def replace_password(
    old_password: str,
    new_password: str,
    response: Response,
    user: Users = Depends(get_current_user),
):
    "Замена пароля"
    return await replace_old_password(old_password, new_password, user, response)
