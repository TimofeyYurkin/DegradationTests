from flask import jsonify
from flask_restful import abort, reqparse, Resource
from . import db_session
from .question_model import Question

parser = reqparse.RequestParser()
parser.add_argument('test_id', required=True, type=int)
parser.add_argument('text', required=True, type=str)


def abort_if_question_not_found(question_id):
    session = db_session.create_session()
    question = session.query(Question).get(question_id)
    if not question:
        abort(404, message=f'Question {question_id} not found')


class QuestionResource(Resource):
    def get(self, question_id):
        abort_if_question_not_found(question_id)
        session = db_session.create_session()
        question = session.query(Question).get(question_id)
        return jsonify({'question': question.to_dict(only=('test_id', 'text'))})

    def delete(self, question_id):
        abort_if_question_not_found(question_id)
        session = db_session.create_session()
        question = session.query(Question).get(question_id)
        session.delete(question)
        session.commit()
        return jsonify({'success': 'OK'})


class QuestionListResource(Resource):
    def get(self):
        session = db_session.create_session()
        questions = session.query(Question).all()
        return jsonify({'questions': item.to_dict(only=('id', 'test_id', 'text')) for item in questions})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        question = Question(
            test_id=args['test_id'],
            text=args['text']
        )
        session.add(question)
        session.commit()
        return jsonify({'question': question.id})