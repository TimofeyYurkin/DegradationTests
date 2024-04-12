from flask import jsonify
from flask_restful import abort, reqparse, Resource
from . import db_session
from .results_model import Results

parser = reqparse.RequestParser()
parser.add_argument('comment_1', required=True, type=str)
parser.add_argument('comment_2', required=True, type=str)
parser.add_argument('comment_3', required=True, type=str)
parser.add_argument('comment_4', required=True, type=str)


def abort_if_result_not_found(result_id):
    session = db_session.create_session()
    result = session.query(Results).get(result_id)
    if not result:
        abort(404, message=f'Result {result_id} not found')


class ResultResource(Resource):
    def get(self, result_id):
        abort_if_result_not_found(result_id)
        session = db_session.create_session()
        result = session.query(Results).get(result_id)
        return jsonify({'result': result.to_dict(only=('comment_1', 'comment_2', 'comment_3', 'comment_4'))})

    def delete(self, result_id):
        abort_if_result_not_found(result_id)
        session = db_session.create_session()
        result = session.query(Results).get(result_id)
        session.delete(result)
        session.commit()
        return jsonify({'success': 'OK'})


class ResultListResource(Resource):
    def get(self):
        session = db_session.create_session()
        results = session.query(Results).all()
        return jsonify({'results': item.to_dict(only=('id', 'comment_1', 'comment_2', 'comment_3', 'comment_4'))
                        for item in results})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        result = Results(
            comment_1=args['comment_1'],
            comment_2=args['comment_2'],
            comment_3=args['comment_3'],
            comment_4=args['comment_4']
        )
        session.add(result)
        session.commit()
        return jsonify({'result': result.id})