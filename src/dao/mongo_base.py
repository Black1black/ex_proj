from src.utils.repository import AbstractRepository


class BaseDAOmongo(AbstractRepository):
    collection = None

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        collection = cls.collection
        count = await collection.count_documents(filter_by)
        if count == 0:
            return None
        elif count > 1:
            raise Exception("Multiple documents found")

        else:
            return await collection.find_one(filter_by)

    @classmethod
    async def find_all(cls, **filter_by):
        results = await cls.collection.find(filter_by).to_list(None)
        return results

    @classmethod
    async def add(cls, data):
        result = await cls.collection.insert_one(data)
        return result.inserted_id

    @classmethod
    async def delete(cls, **filter_by):
        result = await cls.collection.delete_many(filter_by)
        return result.deleted_count

    @classmethod
    async def update(cls, filter_by, update_data):
        result = await cls.collection.update_many(filter_by, {"$set": update_data})
        return result.modified_count
