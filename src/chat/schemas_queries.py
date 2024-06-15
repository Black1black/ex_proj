# from datetime import datetime
# from enum import Enum, unique

from pydantic import BaseModel, Field
# from bson import ObjectId

# from app.chat.schemas_collections import SMessageBody

# добавить валидацию через ObjectId, а не через str



################# Типизация запросов в коллекции #################


# class SGetMessages(BaseModel):
#     receiver: int
#     message_id: str | None = Field(default=None, alias='messageId')
#
#     class Config:  
#         populate_by_name = True


class SMessagesUpdate(BaseModel):
    'Обновление статуса одного или нескольких сообщений'
    _id: str | list[str] # ObjectId
    read: bool | None
    delete: bool | None

    class Config: 
        populate_by_name = True