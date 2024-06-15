from typing import List
from datetime import datetime

from fastapi import APIRouter, Form, UploadFile, File, WebSocket

from src.auth.dependencies import get_current_user
from src.chat.mongo_dao.messages_dao import MessagesDAO
from src.chat.mongo_dao.user_dialogs_dao import UserDialogsDAO
from src.chat.schemas_queries import SMessagesUpdate
from src.config import settings

from src.databases.redisdb import sub, redis
from src.databases.s3_storage import upload_on_storage
from src.users.models import Users
from fastapi import Depends

from src.chat.schemas_collections import SMessage, ObjectIdField, SMessageBody, SFastDialog

import asyncio

router = APIRouter(prefix='/chat', tags=['Чат'])


# WebSocket маршрут для обновления в режиме реального времени
@router.websocket("/ws/messages")  # TODO на router
async def websocket_endpoint(websocket: WebSocket):#, user: Users = Depends(get_current_user)):
    "WebSocket маршрут для обновления в режиме реального времени"
    print(1)
    user_id = 1#user.id

    await websocket.accept()

    # TODO Ставим онлайн статус

    # Подписка на канал, специфичный для пользователя
    channel = f"user_{user_id}"

    await sub.subscribe(channel) # Можно добавить и общий канал

    try:
        try:
            while True:



                
                message = await sub.get_message() # Чтение сообщений из Redis PubSub

                if message and message['type'] == 'message':
                    msg = message['data']

                    await websocket.send_text(msg)

                await asyncio.sleep(1)


        except:
            return

    finally:
        
        await sub.unsubscribe(channel) # Отписка от канала Redis PubSub
        # TODO Ставим офлайн статус

        await websocket.close()  # TODO проверить нужно ли

       
 

# --------------------------------------------------------------------------------------------------------------------



@router.post("/message")
async def send_message(text: str | None = Form(None),  # Текст сообщения TODO добавить валидацию размера текста
                       files: List[UploadFile] | None = File(None),
                       # Прикреплённые файлы TODO добавить валидацию и ограничение количества
                       receiver: int = Form(),  # Получатель
                       reply_id: ObjectIdField | None = Form(None), # ObjectId
                       publication: str | None = Form(None),  # Ссылка на репост публикации
                       user: Users = Depends(get_current_user)):
    "API маршрут для отправки сообщения"
    user_id = user.id

    # TODO - добавить проверку наличия получателя


    if files:
        uploaded_files_paths = await upload_on_storage(user_id, files, settings.MESSAGE_BUCKET)

    message_body = {
        'files': uploaded_files_paths if files else None,
        'text': text,
        'publication': publication
    }

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

    channel = f"user_{receiver}" # Отправляем сообщение получателю

    insert = message_insert.model_dump_json(by_alias=True)


    await redis.publish(channel, insert)

    return {"status": "Message sent"}


# --------------------------------------------------------------------------------------------------------------------


@router.get("/message")
async def get_one_message(message_id: ObjectIdField, # ObjectId
                          user: Users = Depends(get_current_user)) -> SMessage | None:  
    "Получение отдельного сообщения"
    user_id = user.id
    message = await MessagesDAO.find_one_message(message_id, user_id)
    return message


# --------------------------------------------------------------------------------------------------------------------


@router.patch("/message") 
async def edit_message(messages_data: SMessagesUpdate, user: Users = Depends(get_current_user)):
    'Редактирование (удаление) отдельного сообщения'
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
async def get_dialogs(last_message_datetime: datetime | None = None,
                      user: Users = Depends(get_current_user)) -> list[SFastDialog]:
    "Эндпоинт получения всех диалогов пользователя, время сообщения используется для пагинации диалогов (В списке диалогов есть последнее сообщение и его дата отправки)"
    # TODO - добавить логику получения фото и имени собеседника
    user_id = user.id
    dialogs = await UserDialogsDAO.get_user_dialogs(user_id, last_message_datetime)

    return dialogs

