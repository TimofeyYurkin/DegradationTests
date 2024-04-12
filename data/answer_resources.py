from flask import jsonify
from flask_restful import abort, reqparse, Resource
from . import db_session
from .answer_model import Answer

parser = reqparse.RequestParser()
parser.add_argument('question_id', required=True, type=int)
parser.add_argument('text', required=True, type=str)
parser.add_argument('result', required=True, type=int)


def abort_if_answer_not_found(answer_id):
    session = db_session.create_session()
    answer = session.query(Answer).get(answer_id)
    if not answer:
        abort(404, message=f'Answer {answer_id} not found')


class AnswerResource(Resource):
    def get(self, answer_id):
        abort_if_answer_not_found(answer_id)
        session = db_session.create_session()
        answer = session.query(Answer).get(answer_id)
        return jsonify({'answer': answer.to_dict(only=('question_id', 'text', 'result'))})

    def delete(self, answer_id):
        abort_if_answer_not_found(answer_id)
        session = db_session.create_session()
        answer = session.query(Answer).get(answer_id)
        session.delete(answer)
        session.commit()
        return jsonify({'success': 'OK'})


class AnswerListResource(Resource):
    def get(self):
        session = db_session.create_session()
        answers = session.query(Answer).all()
        return jsonify({'answers': item.to_dict(only=('id', 'question_id', 'text', 'result')) for item in answers})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        answer = Answer(
            question_id=args['question_id'],
            text=args['text'],
            result=args['result']
        )
        session.add(answer)
        session.commit()
        return jsonify({'answer': answer.id})