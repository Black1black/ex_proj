from src.databases.mongodb import db

messages_collection = db["messages"]
dialogs_collection = db["dialogs"]
user_dialogs_collection = db["user_dialogs_collection"]
