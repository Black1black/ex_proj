from src.chat.collections import dialogs_collection
from src.dao.mongo_base import BaseDAOmongo



class DialogsDAO(BaseDAOmongo):
    collection = dialogs_collection
