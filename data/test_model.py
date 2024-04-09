import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Test(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tests'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    type = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    creator = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    cover = sqlalchemy.Column(sqlalchemy.BINARY, nullable=False)
    questions = sqlalchemy.Column(sqlalchemy.BINARY, nullable=False)
    answers = sqlalchemy.Column(sqlalchemy.BINARY, nullable=False)
    results = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('results.id'))
    status = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)

    result = sqlalchemy.orm.relationship('Results')
