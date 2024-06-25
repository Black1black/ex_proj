from geoalchemy2.types import (
    Geography,  # Geometry менее точный чем Geography, он не учитывает сферичность земли, использует плоскую модель
)
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
    or_,
    text,
)
from sqlalchemy.orm import validates

from src.databases.postgres import Base


class Users(Base):
    __tablename__ = 'users'


    id = Column(Integer, primary_key=True, nullable=False)
    phone = Column(Integer, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String, nullable=False)
    status = Column(String, nullable=False, server_default=text("'new'"))
    date_reg = Column(DateTime, nullable=False, server_default=func.now())
    name = Column(String, nullable=False)
    photo = Column(String)
    text = Column(String) 

    @validates('phone', 'email')
    def validate_phone_or_email(self, key, value):
        if not value:
            raise ValueError('Either phone or email must be provided')
        return value

    __table_args__ = (
        CheckConstraint(status.in_(['new', 'active', 'archive', 'banned']), name='chk_users_status'), # TODO реализовать использование статусов
        CheckConstraint(or_(phone != None, email != None), name='chk_users_phone_or_email'),


    )



class UsersLocation(Base):
    __tablename__ = 'users_location'
    user_id = Column(ForeignKey('users.id'), primary_key=True, nullable=False)

    location = Column(Geography(geometry_type='POINT', srid=4326)) 


