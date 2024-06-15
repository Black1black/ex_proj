

from pymongo import IndexModel
from src.databases.mongodb import db


async def ensure_collection_exists(collection_name, indexes=None):
    'Проверка наличия коллекций в БД, при отсутствии - создание индексов и коллекции'
    collections = await db.list_collection_names()
    if collection_name in collections:
        print(f"Коллекция '{collection_name}' уже существует")
        return db[collection_name]

    collection = db[collection_name]
    # await collection.create_indexes([IndexModel(index) for index in (indexes or [])])
    if indexes:
        await collection.create_indexes([IndexModel([index]) for index in (indexes or [])])

    print(f"Коллекция '{collection_name}' создана")
    return collection



async def init_mongo_collections():
    'Функция инициализации индексов и коллекций в mongo_db'
    # await ensure_collection_exists("users")
    # await ensure_collection_exists("messages", [("receiver", 1), ("read", 1)]) TODO добавить индекс по диалог айди
# TODO добавить инициализации коллекций

# Запись индекса в виде ("receiver", 1) означает, что вы создаете индекс по полю "receiver" в порядке возрастания.
#
# Индексы в MongoDB позволяют ускорить поиск данных в коллекции. Поиск по индексностим полям будет выполняться быстрее, чем поиск без индекса.
#
# В данном случае, создание индекса по полю "receiver" сортирует документы в коллекции по значению этого поля в порядке возрастания. Это позволяет эффективно выполнять запросы, которые включают фильтрацию или сортировку по этому полю.
#
# Такие индексы особенно полезны, если у вас есть запросы, которые часто фильтруют или сортируют данные по полю "receiver".
#
# Обратите внимание, что когда значение сортировочного поля (в данном случае, "receiver") повышается, это считается возрастающим порядком (1). Если значение сортировочного поля убывает, это считается убывающим порядком (-1).