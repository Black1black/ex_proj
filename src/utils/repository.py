from abc import ABC, abstractmethod

class AbstractRepository(ABC):
    'Абстрактный класс для реализации работы sqlalchemy и mongo_db'

    @abstractmethod
    async def find_one_or_none(self):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError

    @abstractmethod
    async def add(self):
        raise NotImplementedError

    @abstractmethod
    async def delete(self):
        raise NotImplementedError

    @abstractmethod
    async def data_update(self):
        raise NotImplementedError
