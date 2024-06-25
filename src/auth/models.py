from sqlalchemy import (
    Column,
    ForeignKey,
    String,
)


from src.databases.postgres import Base


class AuthToken(Base): # Класс нашей таблицы
    __tablename__ = 'auth_token'
    'Таблица где храним refresh token'

    token = Column(String, primary_key=True, nullable=False)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    
    # expire = Column(DateTime, nullable=False)
