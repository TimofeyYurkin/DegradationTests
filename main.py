from flask import Flask
from flask_restful import Api
from data import db_session, user_resources, test_resources


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

api = Api(app)

def main():
    # Ресурсы для пользователя
    api.add_resource(user_resources.UserResource, '/api/users/<int:user_id>')
    api.add_resource(user_resources.UserListResource, '/api/users')

    # Ресурсы для тестов
    api.add_resource(test_resources.TestResource, '/api/tests/<int:test_id>')
    api.add_resource(test_resources.TestListResource, '/api/tests')

    db_session.global_init('db/degradation_tests.db')
    app.run(port=8080)


if __name__ == '__main__':
    main()