import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Question(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    test_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('tests.id'), nullable=False)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    test = sqlalchemy.orm.relationship('Test')
    answer = sqlalchemy.orm.relationship('Answer', back_populates='question')