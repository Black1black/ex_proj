from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, model_validator, constr
from geoalchemy2 import WKTElement  # Если нужно использовать специфичный тип Geography

# TODO - прописать алиасы


class SUsersAuth(BaseModel):
    'Схема данных для авторизации'
    # phone: int | None
    # Временно отключил т.к. пока регистрация будет только по почте
    email: EmailStr #| None
    password: str

    @model_validator(mode='before')
    def one_of_the_fields_must_be_defined(cls, values):
        'Проверка наличия либо телефона, либо email'
        if not (values.get('phone') or values.get('email')):
            raise ValueError('At least one of the phone or email fields must be defined')
        return values



    class Config:
            populate_by_name = True



class SUsersReg(SUsersAuth):
    'Схема данных для регистрации, расширена от схемы аутентификации'

    name: str



# Определение Enum для статусов
class UserStatus(str, Enum):
    NEW = 'new'
    ACTIVE = 'active'
    BUSINESS = 'business'
    ARCHIVE = 'archive'
    BANNED = 'banned'

class SUsersGet(BaseModel):
    'Схема данных для передачи данных пользователя на фронтенд'
    id: int
    # phone: int | None
    # email: EmailStr | None
    # hashed_password: str ##
    status: UserStatus # constr(regex='^(new|active|business|archive|banned)$')
    date_reg: datetime
    name: str
    photo: str | None
    text: str | None
    # location: WKTElement | None
    distance: float
    online: bool



    class Config: # TODO нужно чтобы pydantic распознал схему алхимии  (1.6 последнее видео) // смотри на нашу модель не только как словарь, но и на класс у которого есть аттрибуты
            populate_by_name = True




class SUsersMyInfo(BaseModel):
    'Схема данных для получения информации о текущем пользователе'

    id: int
    phone: int | None
    email: EmailStr | None
    # hashed_password: str ##
    status: UserStatus # constr(regex='^(new|active|business|archive|banned)$')
    date_reg: datetime
    name: str
    photo: str | None
    text: str | None
    # location: WKTElement | None # TODO реализовать валидацию этого типа


    @model_validator(mode='before')
    def one_of_the_fields_must_be_defined(cls, values):
        'Проверка наличия либо телефона, либо email'
        if not (values.get('phone') or values.get('email')):
            raise ValueError('At least one of the phone or email fields must be defined')
        return values


class SLocation(BaseModel):
    'Схема для получения данных о локации'
    latitude: str
    longitude: str