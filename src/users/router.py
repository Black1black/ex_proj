
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi_cache.decorator import cache


from src.auth.dependencies import get_current_user
from src.chat.constants import online_list
from src.config import settings
from src.databases.s3_storage import S3Client
from src.exceptions import NullDataException, UsersNotExistsException
from src.tasks.tasks import delete_old_pic
from src.users.dao import UsersDAO
from src.users.models import Users
from src.users.schemas import SLocation, SUsersGet, SUsersMyInfo
from src.users.services import create_point
from src.utils.redis_utils import find_in_redis_list

router = APIRouter(prefix='/users', tags=['Пользователи'])


@router.get("/user")
@cache(expire=60)
async def get_my_info(
        user: Users = Depends(get_current_user)) -> SUsersMyInfo:  # испраить - другая схема - различные варианты
    'Получить модель текущего пользователя'
    return user



@router.get("/user{id}")
@cache(expire=60)
async def get_user_info(id: int,
                        latitude: str | None = None,
                        longitude: str | None = None,
                        ) -> SUsersGet:
    'Получить модель другого пользователя'

    if latitude and longitude:
        location = create_point(SLocation(latitude=latitude, longitude=longitude))
    else:
        location = None

    online = await find_in_redis_list(online_list, id)
    user = await UsersDAO.find_user(id=id, online=online, my_location=location)
    if not user:
        raise UsersNotExistsException
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
        uploaded_files_paths = await S3Client(settings.PROFILE_BUCKET).upload_on_storage(user_id, files)
        if uploaded_files_paths:
            photo = uploaded_files_paths[0] # функция возвращает нам список всегда, поэтому вытаскиваем первый ссылочный элемент
            # process_pic.delay(uploaded_files_paths[0]) # task TODO Реализовать систему изменения размерности с сохранением в S3

    variables = {
        'name': name,
        'text': text,
        'photo': photo
    }

    data_update = {k: v for k, v in variables.items() if v is not None}
    # В данные для изменения попадают только не пустые значения

    if not data_update:
        raise NullDataException

    await UsersDAO.data_update(user_id, **data_update)
    if photo and user.photo:
        delete_old_pic.delay(user.photo, settings.PROFILE_BUCKET) # запустили таску на удаление старого фото из s3

    return {'message': 'success'}



@router.patch("/location")
async def update_location(latitude: str | None,
                          longitude: str | None,
                          user: Users = Depends(get_current_user)):
    'Изменение информации о локации'
    user_id = user.id
    location = create_point(SLocation(latitude=latitude, longitude=longitude))

    await UsersDAO.location_update(user_id, location)
    return {'message': 'success'}

