import asyncio
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, File, Form, UploadFile, WebSocket
from fastapi_cache.decorator import cache

from src.auth.dependencies import get_current_user
from src.chat.constants import online_list
from src.chat.mongo_dao.messages_dao import MessagesDAO
from src.chat.mongo_dao.user_dialogs_dao import UserDialogsDAO
from src.chat.schemas_collections import (
    ObjectIdField,
    SFastDialog,
    SMessage,
    SMessageBody,
)
from src.chat.schemas_queries import SMessagesUpdate
from src.config import settings
from src.databases.redisdb import RedisConnect
from src.databases.s3_storage import S3Client
from src.exceptions import NullDataException
from src.users.models import Users

router = APIRouter(prefix='/chat', tags=['Чат'])


@router.websocket("/ws/messages")
async def websocket_endpoint(websocket: WebSocket, user: Users = Depends(get_current_user)):
    "WebSocket маршрут для обновления в режиме реального времени"
    user_id = user.id

    await websocket.accept()

    # Подписка на канал пользователя
    channel = f"user_{user_id}"

    redis_connect=RedisConnect()

    async with redis_connect.get_redis_client() as redis_client:
        await redis_client.lpush(online_list, user_id)  # Добавляем пользователя в онлайн список
        async with redis_connect.get_pubsub_client(redis_client) as pubsub:
            await pubsub.subscribe(channel)  # Подписка на канал пользователя

            try:
                while True:
                    message = await pubsub.get_message()  # Чтение сообщений из Redis Pub/Sub

                    if message and message.get('type') == 'message':
                        msg = message['data']
                        await websocket.send_text(msg)

                    await asyncio.sleep(1)

            except Exception as e:
                print(f"WebSocket error: {e}")
            finally:
                await pubsub.unsubscribe(channel)  # Отписка от канала Redis Pub/Sub
                await redis_client.lrem(online_list, 0, user_id)  # Удаляем пользователя из онлайн списка
                await websocket.close()

       
 

# --------------------------------------------------------------------------------------------------------------------



@router.post("/message")
async def send_message(text: str | None = Form(None),  # Текст сообщения TODO добавить валидацию размера текста
                       files: List[UploadFile] | None = File(None), # TODO добавить валидацию и ограничение количества
                       receiver: int = Form(),
                       reply_id: ObjectIdField | None = Form(None),
                       user: Users = Depends(get_current_user)):
    "Отправляем сообщение"
    user_id = user.id

    # TODO - добавить проверку наличия получателя

    uploaded_files_paths = None
    if files:
        uploaded_files_paths = await S3Client.upload_on_storage(user_id, files, settings.MESSAGE_BUCKET)

    message_body = {
        'files': uploaded_files_paths,
        'text': text,
    }

    if not uploaded_files_paths and not text:
        raise NullDataException

    dialog_id = await UserDialogsDAO.find_dialogs_id(user_id, receiver)

    upload_data = {
        'dialog_id': dialog_id,
        'sender': user_id,
        'receiver': receiver,
        'reply_id': reply_id,
        'message_body': SMessageBody(**message_body)
    }


    message = SMessage(**upload_data).model_dump(by_alias=True, exclude='_id')


    message_insert = await MessagesDAO.save_message_to_db(message)

    channel = f"user_{receiver}"

    insert = message_insert.model_dump_json(by_alias=True)

    async with RedisConnect().get_redis_client() as redis_client:
        await redis_client.publish(channel, insert)

    return {"status": "Message sent"}


# --------------------------------------------------------------------------------------------------------------------


@router.get("/message")
async def get_one_message(message_id: ObjectIdField,
                          user: Users = Depends(get_current_user)) -> SMessage | None:  
    "Получение отдельного сообщения"
    user_id = user.id
    message = await MessagesDAO.find_one_message(message_id, user_id)
    return message


# --------------------------------------------------------------------------------------------------------------------


@router.patch("/message") 
async def edit_message(messages_data: SMessagesUpdate, user: Users = Depends(get_current_user)):
    'Редактирование (удаление) отдельного сообщения и проставление статуса "прочитано"'
    user_id = user.id
    result = await MessagesDAO.update_messages(messages_data, user_id)
    return result


# --------------------------------------------------------------------------------------------------------------------


@router.get("/messages_before")
async def get_messages_before_dialog_id(receiver: int, message_id: ObjectIdField | None = None,
                                        user: Users = Depends(get_current_user)) -> list[SMessage]:
    'Поиск сообщений в диалоге с пагинацией (поиск до указанного message_id)'

    user_id = user.id
    dialog_id = await UserDialogsDAO.find_dialogs_id(user_id, receiver)
    messages = await MessagesDAO.find_messages_before_message_id(dialog_id=dialog_id, start_id=message_id)

    return messages


# --------------------------------------------------------------------------------------------------------------------


@router.get("/messages_after")
async def get_messages_after_dialog_id(receiver_id: int, message_id: ObjectIdField | None = None,
                                       user: Users = Depends(get_current_user)) -> list[SMessage]:
    'Поиск сообщений в диалоге с пагинацией (поиск после указанного message_id)'
    user_id = user.id
    dialog_id = await UserDialogsDAO.find_dialogs_id(user_id, receiver_id)
    messages = await MessagesDAO.find_messages_after_message_id(dialog_id=dialog_id, start_id=message_id)

    return messages


# --------------------------------------------------------------------------------------------------------------------


@router.get("/dialogs")
@cache(expire=60)
async def get_dialogs(last_message_datetime: datetime | None = None,
                      user: Users = Depends(get_current_user)) -> list[SFastDialog]:
    """Эндпоинт получения всех диалогов пользователя, время сообщения используется для пагинации диалогов
    (В списке диалогов есть последнее сообщение и его дата отправки)"""
    user_id = user.id
    dialogs = await UserDialogsDAO.get_user_dialogs(user_id, last_message_datetime)

    return dialogs

