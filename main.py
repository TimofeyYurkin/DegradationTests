from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from requests import get, post, delete
from data import db_session, user_resources, test_resources, question_resources, answer_resources, results_resources
from forms.user_forms import RegisterForm, LoginForm, DeleteForm
from forms.test_forms import TestPercentForm, TestNumbersForm
from data.user_model import User


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    # Ресурсы для пользователя
    api.add_resource(user_resources.UserResource, '/api/users/<int:user_id>')
    api.add_resource(user_resources.UserListResource, '/api/users')

    # Ресурсы для тестов
    api.add_resource(test_resources.TestResource, '/api/tests/<int:test_id>')
    api.add_resource(test_resources.TestListResource, '/api/tests')

    # Ресурсы для вопросов
    api.add_resource(question_resources.QuestionResource, '/api/questions/<int:question_id>')
    api.add_resource(question_resources.QuestionListResource, '/api/questions')

    # Ресурсы для ответов
    api.add_resource(answer_resources.AnswerResource, '/api/answers/<int:answer_id>')
    api.add_resource(answer_resources.AnswerListResource, '/api/answers')

    # Ресурсы для результатов
    api.add_resource(results_resources.ResultResource, '/api/results/<int:result_id>')
    api.add_resource(results_resources.ResultListResource, '/api/results')

    db_session.global_init('db/degradation_tests.db')
    app.run(port=8080)


# Основной route
@app.route('/')
def index():
    return render_template('tests_list.html', title='DegradationTests')


# Пользовательские route'ы
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        session = db_session.create_session()

        # Проверка необходимых условий для создания пользователя
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form, message="Такая почта уже занята")

        # Добавления пользователя в базу данных
        user_id = post('http://127.0.0.1:8080/api/users', json={
            'name': form.name.data,
            'email': form.email.data,
            'password': form.password.data
        }).json()['id']
        user = session.query(User).get(user_id)
        login_user(user, remember=True)
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        # Проверка соответствия указанных данных
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', title='Авторизация', form=form, message='Неправильная почта или пароль')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/delete_user', methods=['GET', 'POST'])
def delete_user():
    form = DeleteForm()
    if form.validate_on_submit():

        # Проверка соответствия указанных данных
        if current_user.email == form.email.data and current_user.check_password(form.password.data):
            delete(f'http://127.0.0.1:8080/api/users/{current_user.id}')
            return redirect('/')
        return render_template('delete_user.html', title='Удаление', form=form, message='Неправильная почта или пароль')
    return render_template('delete_user.html', title='Удаление', form=form)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


# Тестовые route'ы
@app.route('/choose_type')
@login_required
def choose_type():
    return render_template('tests_types.html', title='Выбор типа теста')


@app.route('/choose_type/<int:test_type>', methods=['GET', 'POST'])
@login_required
def make_test(test_type):
    if test_type == 1:
        form = TestNumbersForm()
    elif test_type == 2 or test_type == 3:
        form = TestPercentForm()
    if request.method == 'POST':
        # Добавляю в БД основную информацию о тесте и получаю id для дальнейшего использования
        test_id = post('http://127.0.0.1:8080/api/tests', json={
            'type': test_type,
            'creator': current_user.id,
            'title': form.test_title.data,
            'description': form.test_description.data,
            'status': form.privacy.data
        }).json()['test']

        # Пробегаюсь по всем вопросам и ответам для них и добавляю в БД
        for position, question in enumerate(form.questions, start=1):
            question_id = post('http://127.0.0.1:8080/api/questions', json={
                'test_id': test_id,
                'position': position,
                'text': question.title.data
            }).json()['question']

            post('http://127.0.0.1:8080/api/answers', json={
                'question_id': question_id,
                'text': question.answer_1.data,
                'result': question.choose_num_1.data if test_type == 1 else question.choose_per_1.data
            })

            post('http://127.0.0.1:8080/api/answers', json={
                'question_id': question_id,
                'text': question.answer_2.data,
                'result': question.choose_num_2.data if test_type == 1 else question.choose_per_2.data
            })

            post('http://127.0.0.1:8080/api/answers', json={
                'question_id': question_id,
                'text': question.answer_3.data,
                'result': question.choose_num_3.data if test_type == 1 else question.choose_per_3.data
            })

            post('http://127.0.0.1:8080/api/answers', json={
                'question_id': question_id,
                'text': question.answer_4.data,
                'result': question.choose_num_4.data if test_type == 1 else question.choose_per_4.data
            })

        # Добавляю в БД результаты
        post('http://127.0.0.1:8080/api/results', json={
            'comment_1': form.result_num_1.data if test_type == 1 else form.result_per_1.data,
            'comment_2': form.result_num_2.data if test_type == 1 else form.result_per_2.data,
            'comment_3': form.result_num_3.data if test_type == 1 else form.result_per_3.data,
            'comment_4': form.result_num_4.data if test_type == 1 else form.result_per_4.data,
        })
        return redirect('/')
    if test_type == 1:
        return render_template('create_test_t1.html', title='Создание теста', form=form)
    elif test_type == 2:
        return render_template('create_test_t2.html', title='Создание теста', form=form)
    elif test_type == 3:
        return render_template('create_test_t3.html', title='Создание теста', form=form)


if __name__ == '__main__':
    main()