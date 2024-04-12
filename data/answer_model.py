import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Answer(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'answers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    question_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('questions.id'), nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    result = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    question = sqlalchemy.orm.relationship('Question')