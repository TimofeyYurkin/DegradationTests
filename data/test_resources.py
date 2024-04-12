from flask import jsonify
from flask_restful import abort, reqparse, Resource
from . import db_session
from .test_model import Test

parser = reqparse.RequestParser()
parser.add_argument('type', required=True, type=int)
parser.add_argument('creator', required=True, type=int)
parser.add_argument('title', required=True, type=str)
parser.add_argument('description', required=True, type=str)
parser.add_argument('status', required=True, type=bool)


def abort_if_test_not_found(test_id):
    session = db_session.create_session()
    test = session.query(Test).get(test_id)
    if not test:
        abort(404, message=f'Test {test_id} not found')


class TestResource(Resource):
    def get(self, test_id):
        abort_if_test_not_found(test_id)
        session = db_session.create_session()
        test = session.query(Test).get(test_id)
        return jsonify({'test': test.to_dict(only=('type', 'creator', 'title', 'description', 'status'))})

    def delete(self, test_id):
        abort_if_test_not_found(test_id)
        session = db_session.create_session()
        test = session.query(Test).get(test_id)
        session.delete(test)
        session.commit()
        return jsonify({'success': 'OK'})


class TestListResource(Resource):
    def get(self):
        session = db_session.create_session()
        tests = session.query(Test).all()
        return jsonify({'tests': item.to_dict(only=('id', 'type', 'creator', 'title', 'description', 'status'))
                        for item in tests})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        test = Test(
            type=args['type'],
            creator=args['creator'],
            title=args['title'],
            description=args['description'],
            status=args['status']
        )
        session.add(test)
        session.commit()
        return jsonify({'test': test.id})