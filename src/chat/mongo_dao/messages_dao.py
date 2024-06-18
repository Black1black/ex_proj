
from src.chat.collections import messages_collection, user_dialogs_collection
from src.chat.schemas_collections import SUserDialog, SFastDialog, SMessage
from src.dao.mongo_base import BaseDAOmongo
from src.databases.mongodb import client
from src.users.dao import UsersDAO




async def update_active_dialogs(user_id, receiver_id, message, s):
    "Обновление активного диалога пользователя"

    # Проверка, существует ли пользователь
    check_user = await user_dialogs_collection.find_one({"_id": user_id}, session=s)

    if check_user:
        # Проверяем, инициирован ли диалог с пользователем
        # existing_dialog = await user_dialogs_collection.find_one({"_id": user_id, "activeDialogs": {"$elemMatch": {"receiverId": receiver_id}}}, session=s)
        existing_dialog = None

        for dialog in check_user.get('activeDialogs', []):  # dialogs_list - ваш массив диалогов
            if dialog.get('receiverId') == receiver_id:
                existing_dialog = dialog
                break



        if existing_dialog:

            # existing_dialog['lastMessage'] = message

            # Обновляем last_message в найденном диалоге и перемещаем его в начало массива
            await user_dialogs_collection.update_one(
                {"_id": user_id, "activeDialogs.receiverId": receiver_id},
                {"$set": {"activeDialogs.$.lastMessage": message},
                 # "$pull": {"activeDialogs": {"receiverId": receiver_id}},
                 # "$push": {"activeDialogs": {"$each": [existing_dialog,], "$position": 0}}
                 },
                # {"_id": user_id, "activeDialogs.receiverId": receiver_id},
                # {"$set": {"activeDialogs.$.lastMessage": message},
                # "$pull": {"activeDialogs": {"receiverId": receiver_id}},
                # "$push": {"activeDialogs": {"$each": [existing_dialog['activeDialogs'][0]], "$position": 0}}
                # },

             # {"_id": user_id, "activeDialogs.receiverId": receiver_id},
                # {"$set": {"active_dialogs.$.last_message": message},
                #  "$pull": {"active_dialogs": {"receiver_id": receiver_id}},
                #  "$push": {"active_dialogs": {"$each": [existing_dialog['active_dialogs'][0]], "$position": 0}}
                #  },
                session=s
            )


        else:
            # Добавляем новый диалог в начало active_dialogs
            receiver = await UsersDAO.find_one_or_none(id=receiver_id)
            receiver_name = receiver.name
            receiver_photo = receiver.photo
            # Создаем SFastDialog объект вместо просто message
            # Не забываем продублировать фото и имя получателя
            new_dialog = SFastDialog(
                dialog_id=message["dialogId"],
                receiver_id=receiver_id,  # добавить receiver_id
                receiver_name=receiver_name,
                receiver_photo=receiver_photo,
                last_message=message
            )
            await user_dialogs_collection.update_one(
                {"_id": user_id},
                {"$push": {"activeDialogs": {"$each": [new_dialog.model_dump(by_alias=True)], "$position": 0}}},
                session=s
            )

    else:
        # Создаем новую запись пользователя с диалогом
        receiver = await UsersDAO.find_one_or_none(id=receiver_id)
        receiver_name = receiver.name
        receiver_photo = receiver.photo
        new_dialog = SFastDialog(
                dialog_id=message["dialogId"], # alias
                receiver_id=receiver_id,  # добавить receiver_id
                receiver_name=receiver_name,
                receiver_photo=receiver_photo,
                last_message=message
        )
        new_user_dialog = SUserDialog(_id=user_id, active_dialogs=[new_dialog])
        # print(new_user_dialog.model_dump(include={'_id', 'active_dialogs'}))
        await user_dialogs_collection.insert_one(new_user_dialog.model_dump(by_alias=True), session=s)

#
# {
#   "_id": {
#     "$oid": "655e1b2c46cb6106f1b11368"
#   },
#   "dialogId": "655e1b2c46cb6106f1b11367",
#   "sender": 1,
#   "receiver": 2,
#   "replyId": null,
#   "messageBody": {
#     "files": null,
#     "text": "апрапрапр",
#     "publication": null
#   },
#   "read": false,
#   "sendTime": {
#     "$date": "2023-11-22T15:15:56.525Z"
#   },
#   "delete": false
# }

class MessagesDAO(BaseDAOmongo):
    collection = messages_collection

    @classmethod
    async def find_one_message(cls, message_id, user_id):
        'Поиск одного конкретного сообщения'

        message = await cls.collection.find_one(
            {'_id': message_id,
             '$or': [
                 {'sender': user_id},
                 {'receiver': user_id}
             ]}
        )
        print(type(message_id), message)
        return message

    # @classmethod
    # async def find_messages(cls, dialog_id, limit=26, start_id=None):
    #     'Поиск сообщений в диалоге с пагинацией'
    #
    #     conditions = {'dialog_id': dialog_id}
    #     if start_id is not None:
    #         conditions['_id'] = {'$lt': start_id}
    #
    #     messages = await cls.collection.find(conditions).sort('_id', -1).limit(limit).to_list(length=limit)
    #     messages = messages[::-1]
    #
    #     return messages

    @classmethod
    async def find_messages_before_message_id(cls, dialog_id, limit=15, start_id=None):
        'Поиск сообщений в диалоге с пагинацией (поиск после указанного message_id)'

        conditions = {'dialogId': str(dialog_id)}
        if start_id is not None:
            conditions['_id'] = {'$gt': start_id}

        pipeline = [
            {'$match': conditions},
            {'$limit': limit},
        ]

        messages = await cls.collection.aggregate(pipeline).to_list(length=limit)

        return messages
    

    @classmethod
    async def find_messages_after_message_id(cls, dialog_id, limit=15, start_id=None):
        'Поиск сообщений в диалоге с пагинацией (поиск до указанного message_id)'

        conditions = {'dialogId': str(dialog_id)}
        if start_id is not None:
            conditions['_id'] = {'$lt': start_id}

        pipeline = [
            {'$match': conditions},
            {'$sort': {'_id': -1}},
            {'$limit': limit},
            {'$sort': {'_id': 1}}
        ]

        messages = await cls.collection.aggregate(pipeline).to_list(length=limit)
        # messages = await cls.collection.find().to_list(None)

        # print(messages)


        return messages







    @classmethod
    async def update_messages(cls, data, user_id):
        'Обновление статусов сообщений, или их удаление'
        id = data.get('_id')
        read = data.get('read')
        delete = data.get('delete')

        # Проверяем, является ли пользователь отправителем или получателем сообщения
        message = await cls.collection.find_one({"_id": id})
        if not message:
            raise ValueError("Message with this id does not exist.")

        if delete and message['sender'] == user_id:
            # Пользователь является отправителем и может удалить сообщение
            await cls.collection.update_one({"_id": id}, {"$set": {"delete": True}})
        elif read and message['receiver'] == user_id:
            # Пользователь является получателем и может отметить сообщение как прочитанное
            await cls.collection.update_one({"_id": id}, {"$set": {"read": True}})
        else:
            raise ValueError("User does not have permission to update this message.")

        # TODO - добавить проверку - не является ли это последним сообщением и если да, то нужно также его обновить в диалогах у пользователей и отправлять в вебсокет

        return

    @classmethod
    async def save_message_to_db(cls, message):
        'Сохранение сообщения в бд и обновление последнего сообщения в диалоге'

        async with await client.start_session() as s:
            # Начало транзакции
            s.start_transaction()
            try:
                message_insert = await cls.collection.insert_one(message, session=s)
                result_id = message_insert.inserted_id
                message.update({'_id': result_id})

                # Обновляем диалоги для отправителя и получателя
                # TODO - возможно стоит использовать bulk_write
                await update_active_dialogs(message['sender'], message['receiver'], message, s)
                await update_active_dialogs(message['receiver'], message['sender'], message, s)

                await s.commit_transaction()
                # return result_id, is_new
                # return (message)
                return SMessage(**message)


            except Exception as e:
                await s.abort_transaction()
                raise e


            # except Exception as e:
            #     await s.abort_transaction()
            #     raise e
