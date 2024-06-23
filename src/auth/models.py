from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    or_,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import validates

from src.databases.postgres import Base


class AuthToken(Base): # Класс нашей таблицы
    __tablename__ = 'auth_token'
    'Таблица где храним refresh token'

    token = Column(String, primary_key=True, nullable=False)
    user_id = Column(ForeignKey('users.id'), nullable=False)
    
    # expire = Column(DateTime, nullable=False)
