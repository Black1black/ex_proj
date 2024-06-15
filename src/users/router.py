from typing import List
from datetime import datetime

from fastapi import APIRouter, Form, UploadFile, File

from src.auth.dependencies import get_current_user

from src.users.dao import UsersDAO

from src.config import settings

from src.databases.s3_storage import upload_on_storage

from src.users.models import Users
from fastapi import Depends

from src.users.schemas import SUsersGet, SUsersMyInfo

router = APIRouter(prefix='/users', tags=['Пользователи'])


@router.get("/user")
async def get_my_info(
        user: Users = Depends(get_current_user)) -> SUsersMyInfo:  # испраить - другая схема - различные варианты
    'Получить модель текущего пользователя'
    return user



@router.get("/user{id}")
async def get_user_info(id: int) -> SUsersGet:  # испраить - другая схема - различные варианты
    'Получить модель другого пользователя'
    user = await UsersDAO.find_user(id=id)

    # TODO добавить информацию об онлайне
    return user



@router.patch("/users")
async def update_info(name: str | None = Form(None),
                      text: str | None = Form(None),
                      files: UploadFile | None = File(None),
                      user: Users = Depends(get_current_user)):
    'Обновление информации пользователя'

    user_id = user.id
    photo = None

    if files:
        uploaded_files_paths = await upload_on_storage(user_id, files, settings.MESSAGE_BUCKET)
        if uploaded_files_paths:
            photo = uploaded_files_paths[0] # функция возвращает нам список всегда, поэтому вытаскиваем первый ссылочный элемент

    variables = {
        'name': name,
        'text': text,
        'photo': photo
    }

    data_update = {k: v for k, v in variables.items() if v is not None}

    if not data_update:
        raise  # TODO - прописать ошибку

    await UsersDAO.data_update(user_id, **data_update)

    return user  # TODO - вернуть инфу .



@router.patch("/location")
async def update_location(location: str, user: Users = Depends(get_current_user)):
    'Изменение информации о локации'
    user_id = user.id



    await UsersDAO.location_update(user_id, location)

#     TODO - везде прописать ретёрны

