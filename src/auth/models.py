from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint, Boolean, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from src.databases.postgres import Base

from sqlalchemy import or_
from sqlalchemy.orm import validates


class AuthToken(Base): # Класс нашей таблицы
    __tablename__ = 'auth_token'
    'Таблица где храним refresh token'

    token = Column(String, primary_key=True, nullable=False)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    
    # expire = Column(DateTime, nullable=False)
