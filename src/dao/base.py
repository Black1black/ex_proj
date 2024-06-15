from src.utils.repository import AbstractRepository
from src.databases.postgres import async_session_maker, engine 
from sqlalchemy import select, insert, delete, update


class BaseDAO(AbstractRepository):
    model = None


    @classmethod
    async def find_one_or_none(cls, **filter_by): 
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            # print(query.compile(engine, compile_kwargs={'literal_binds': True})) # Чтобы увидеть сырой запрос
            result = await session.execute(query)
            return result.scalar_one_or_none() # TODO Преверить, подходит ли мне этот метод

    @classmethod
    async def find_all(cls,  **filter_by):
        async with async_session_maker() as session:  
            query = select(cls.model).filter_by(**filter_by)

            result = await session.execute(query)  
            return result.scalars().all()
            # return result.mappings().all()


    @classmethod
    async def add(cls,  **data):
        async with async_session_maker() as session:
            query = insert(cls.model).values(**data).returning(cls.model.id)
            await session.execute(query)
            await session.commit()


    @classmethod
    async def delete(cls, **filter_by):
        async with async_session_maker() as session:
            query = delete(cls.model).filter_by(**filter_by)

            
            await session.execute(query)
            await session.commit()


    @classmethod
    async def data_update(cls, id, **kwargs):
        async with async_session_maker() as session:
            query = update(cls.model).where(cls.model.id == id).values(**kwargs)
            await session.execute(query)
            await session.commit()

