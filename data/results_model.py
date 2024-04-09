import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Results(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'results'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    comments = sqlalchemy.Column(sqlalchemy.BINARY, nullable=False)
    image_1 = sqlalchemy.Column(sqlalchemy.BINARY, nullable=False)
    image_2 = sqlalchemy.Column(sqlalchemy.BINARY, nullable=False)
    image_3 = sqlalchemy.Column(sqlalchemy.BINARY, nullable=False)
    image_4 = sqlalchemy.Column(sqlalchemy.BINARY, nullable=False)

    test = sqlalchemy.orm.relationship('Test', back_populates='result')