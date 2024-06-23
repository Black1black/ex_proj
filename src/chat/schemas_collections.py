from datetime import datetime
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, Field, conlist
from pydantic_core import core_schema


class ObjectIdField(str):
    'Типизация поля типа ObjectId'
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        object_id_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ]
        )
        return core_schema.json_or_python_schema(
            json_schema=object_id_schema,
            python_schema=core_schema.union_schema(
                [core_schema.is_instance_schema(ObjectId), object_id_schema]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def validate(cls, value):
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid id")

        return ObjectId(value)





#############################################################################
class SMessageBody(BaseModel):
    files: conlist(str, min_length=1, max_length=5) | None  # ссылки на s3
    text: str | None 
    publication: str | None  # ссылка на публикацию контента (репост) // реализация будет позже

    class Config:  
        populate_by_name = True


class SMessage(BaseModel):
    'Типизация отдельного сообщения'
    id: ObjectIdField | None = Field(default=None, alias='_id')

    dialog_id: ObjectIdField = Field(alias='dialogId')
    sender: int
    receiver: int
    reply_id: ObjectIdField | None = Field(default=None, alias='replyId')  # на какое сообщение ответ # ObjectId
    # content_type: SContentChoice = Field(alias='contentType') # TODO добавить выбор из текст картинка, видео, репост
    # content_body: str = Field(alias='contentBody')
    message_body: SMessageBody = Field(alias='messageBody')
    read: bool = False
    send_time: datetime = Field(default_factory=datetime.utcnow, alias='sendTime')  # datetime.utcnow()
    delete: bool = False  # Удалено ли сообщение
    # edit: bool = False  # пока не будет функционала изменения, будет только удаление

    class Config:  
        populate_by_name = True



################# Типизация коллекции диалогов #################
class SDialog(BaseModel):
    'Коллекция диалогов'
    id: ObjectIdField | None = Field(default=None, alias='_id')
    users: list[int]
    delete: bool = False
    delete_date: datetime | None = Field(default=None, alias='deleteTime')

    class Config:  
        populate_by_name = True



################# Типизация списка активных диаалогов пользователя #################
class SFastDialog(BaseModel):
    'Модель диалога и последнего сообщения в диалоге'
    dialog_id: ObjectIdField = Field(alias='dialogId') # ObjectId
    receiver_id: int = Field(alias='receiverId')  # айди собеседника
    receiver_name: str = Field(alias='receiverName')
    receiver_photo: str | None = Field(alias='receiverPhoto') # ссылка на s3 storage

    last_message: SMessage = Field(alias='lastMessage')

    class Config: 
        populate_by_name = True



class SUserDialog(BaseModel):
    'Коллекция активных диалогов пользователя'
    id: int = Field(alias='_id')
    active_dialogs: list[SFastDialog] = Field(alias='activeDialogs')  #

    class Config:
        populate_by_name = True


####################################################################



