import sqlalchemy
from data import db_session
from sqlalchemy import orm
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Good(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'Goods'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    Category_id = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Producer_id = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    Good_name = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    info = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
