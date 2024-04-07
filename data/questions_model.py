import sqlalchemy
from sqlalchemy_file import FileField
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase

class Questions(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    questions = sqlalchemy.Column(FileField, nullable=False)
