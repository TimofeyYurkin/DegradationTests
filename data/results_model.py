import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Results(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'results'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    comment_1 = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    comment_2 = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    comment_3 = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    comment_4 = sqlalchemy.Column(sqlalchemy.String, nullable=False)