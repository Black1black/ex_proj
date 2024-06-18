from src.chat.collections import user_dialogs_collection, dialogs_collection
from src.chat.schemas_collections import SDialog
from src.dao.mongo_base import BaseDAOmongo
from src.databases.mongodb import client



class UserDialogsDAO(BaseDAOmongo):
    collection = user_dialogs_collection

    @classmethod
    async def get_user_dialogs(cls, user_id, last_message_datetime=None, limit=15):
        '''
        Получение всех диалогов пользователя
        с пагинацией, предварительно по дате последнего сообщения с сортировкой
        от самого нового к старому.
        '''
        pipeline = [
            {"$match": {"_id": user_id}},  # Выбор пользователя по id
            {"$unwind": "$activeDialogs"},  # Раскрываем каждый элемент массива activeDialogs в отдельный документ
            {"$sort": {"activeDialogs.lastMessage.sendTime": -1}},  # Сортируем диалоги по дате последнего сообщения
        ]

        if last_message_datetime:
            pipeline.append({"$match": {"activeDialogs.lastMessage.sendTime": {"$lte": last_message_datetime}}})

        pipeline.append({"$replaceRoot": {"newRoot": "$activeDialogs"}})  # Заменяем корень документа на activeDialogs
        pipeline.append({"$limit": limit})  # Ограничиваем количество документов до limit

        result = await cls.collection.aggregate(pipeline).to_list(None)
        # return [SFastDialog(**doc) for doc in result]

        # print(result)
        return result






    @classmethod
    async def find_dialogs_id(cls, user_id, receiver_id):
        "Поиск айди нужного нам диалога"

        async with await client.start_session() as s:
            # Начало транзакции
            s.start_transaction() # TODO - возможно не нужно тут async with
            try:
                pipeline = [
                    {"$match": {"_id": user_id}},
                    {"$unwind": "$active_dialogs"},
                    {"$match": {"active_dialogs.receiver_id": receiver_id}},
                    {"$project": {"_id": 0, "dialog_id": "$active_dialogs.dialog_id"}}
                ]

                result = await cls.collection.aggregate(pipeline, session=s).to_list(length=None)

                # Если диалог найден среди активных диалогов
                if result:
                    return result[0]["dialog_id"] # TODO - может возникнуть ошибка, ведь у нас может вернуться словарь
 
                # Если диалог не найден среди активных диалогов, ищем его в коллекции диалогов
                dialog = await dialogs_collection.find_one(
                    {"users": {"$in": [[user_id, receiver_id], [receiver_id, user_id]]}, "delete": False}, session=s)

                # Если диалог найден в коллекции диалогов, возвращаем его ID
                if dialog:
                    return dialog["_id"]

                else:
                    # Если диалог не найден, создаем новый
                    new_dialog = SDialog(users=[user_id, receiver_id])
                    new_dialog_data = new_dialog.model_dump(exclude={"_id"})
                    result = await dialogs_collection.insert_one(new_dialog_data, session=s)
                    await s.commit_transaction()
                    return result.inserted_id  # Возвращаем ID нового диалога

            except Exception as e:
                # Откатываем транзакцию при возникновении ошибки
                await s.abort_transaction()
                raise e

    