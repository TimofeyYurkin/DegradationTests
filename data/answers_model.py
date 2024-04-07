import sqlalchemy
from sqlalchemy_file import FileField
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase

class Answers(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'answers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    answers = sqlalchemy.Column(FileField, nullable=False)
