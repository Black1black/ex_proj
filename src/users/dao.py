from geoalchemy2 import WKTElement
from sqlalchemy import and_, asc, delete, desc, func, insert, literal, select, update

from src.dao.base import BaseDAO
from src.databases.postgres import async_session_maker
from src.users.models import Users, UsersLocation


class UsersDAO(BaseDAO):
    model = Users

############################################ Auth #############################################
    @classmethod
    async def add_user(cls,  **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data)#.returning(cls.model.id) 
            result = await session.execute(query) 

            # Получение id новой записи
            new_id = result.fetchone()[0]  # Обычно fetchone() возвращает кортеж, где на первой позиции находится id


            # Добавляем местоположение пользователя
            location_query = insert(UsersLocation).values(user_id=new_id)
            await session.execute(location_query)



            await session.commit()


#############################################################################

    @classmethod
    async def find_me(cls, id: int):
        'Поиск модели текущего пользователя'
        async with async_session_maker() as session:


            user = select(cls.model.id,
                          cls.model.phone,
                          cls.model.email,


                          cls.model.status,
                          cls.model.date_reg,
                          cls.model.name,
                          cls.model.photo,
                          cls.model.text).filter_by(cls.model.id==id)

            result = await session.execute(user)
            return result.scalar_one_or_none()  # TODO 
        

    @classmethod
    async def find_user(cls, id: int, online: bool, my_location: WKTElement=None): # TODO добавить корректный тип и показ онлайн
        'Поиск модели другого пользователя'
        online_column = literal(online).label('online')

        if my_location:
            distance_column = func.ST_Distance(UsersLocation.location,
                                               my_location).label('distance')
        else:
            distance_column = literal(-1).label('distance')
        async with async_session_maker() as session:

            query = select(
                distance_column,
                online_column,

                cls.model.id,
                cls.model.status,
                cls.model.date_reg,
                cls.model.name,
                cls.model.photo,
                cls.model.text,
                # TODO добавить столбец дистанции


            ).select_from(cls.model
            ).join(UsersLocation, cls.model.id == UsersLocation.user_id, isouter=True
            ).filter_by(id=id)


            result = await session.execute(query)
            return result.scalar_one_or_none()  # Специальный метод в алхимии // вернётся либо один объект, либо ничего


    @classmethod
    async def location_update(cls, id, location): # Изменение данных
        'Обновление данных о локации пользователя'
        async with async_session_maker() as session:
            query = update(UsersLocation).where(UsersLocation.user_id == id).values(location=location)
            await session.execute(query) # исполняем запрос
            await session.commit() # фиксируем все изменения