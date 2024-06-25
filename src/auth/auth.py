from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext
from pydantic import EmailStr

from src.auth.constants import access_token_name, refresh_token_name
from src.config import settings
from src.exceptions import CannotReplacePasswordException
from src.users.dao import UsersDAO

#------------------------------------------------------------------------------------------#
####################### Хэшируем пароль и проверяем его ####################################


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto') # TODO - вынести в env


def get_password_hash(password: str) -> str:
    '''получаем пароль и возвращаем хешированную версию (функция из документации)'''
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    '''Сравнение переданного пароля и того что хранится в базе (в базе захеширован)'''
    return pwd_context.verify(plain_password, hashed_password)

########################################################################################


async def replace_old_password(old_password, new_password, current_user, response):

    if verify_password(old_password, current_user.hashed_password):
        new_password = get_password_hash(new_password)
        await UsersDAO.data_update(current_user.id, hashed_password=new_password)
        response.delete_cookie(access_token_name)
        response.delete_cookie(refresh_token_name)
        return {'message': 'Вы изменили пароль'}
    else:
        raise CannotReplacePasswordException # TODO Прописать ошибку




#--------------------------------------------------------------------------------------#
#################################### JWT ###############################################

def create_jwt_token(data: dict, is_access: bool = True) -> str:
    'Принимает словарь с данными которые хотим передать в токен и возвращает JWT(str)'
    to_encode = data.copy()
    if is_access:
        times_exp = timedelta(seconds=3600)
    else:
        times_exp = timedelta(days=60)
    expire = datetime.utcnow() + times_exp
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM) # (Что кодируем, ключ, алгоритм)
    
    return encoded_jwt


async def authentificate_user(email: EmailStr, password: str):
    user = await UsersDAO.find_one_or_none(email=email) # Проверяем, есть ли такой пользователь
    print(user)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

