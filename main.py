from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from requests import get, post, delete
from data import db_session, user_resources, test_resources, question_resources, answer_resources, results_resources
from data.test_model import Test
from data.question_model import Question
from data.answer_model import Answer
from data.results_model import Results
from forms.user_forms import RegisterForm, LoginForm, DeleteForm
from forms.test_forms import TestPercentForm, TestNumbersForm, TestPassingForm
from data.user_model import User


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['JSON_SORT_KEYS'] = False

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
    session = db_session.create_session()
    tests = session.query(Test)
    return render_template('tests_list.html', title='DegradationTests', tests=tests)


# Пользовательские route'ы
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        session = db_session.create_session()

        # Проверка необходимых условий для создания пользователя
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='DegradationTests', form=form, message="Пароли не совпадают")
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='DegradationTests', form=form, message="Такая почта уже занята")

        # Добавления пользователя в базу данных
        user_id = post('http://127.0.0.1:8080/api/users', json={
            'name': form.name.data,
            'email': form.email.data,
            'password': form.password.data
        }).json()['id']
        user = session.query(User).get(user_id)
        login_user(user, remember=True)
        return redirect('/')
    return render_template('register.html', title='DegradationTests', form=form)


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
        return render_template('login.html', title='DegradationTests', form=form, message='Неправильная почта или пароль')
    return render_template('login.html', title='DegradationTests', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/delete_user', methods=['GET', 'POST'])
def delete_user():
    form = DeleteForm()
    if form.validate_on_submit():
        if current_user.email == form.email.data and current_user.check_password(form.password.data):
            session = db_session.create_session()
            user_tests = session.query(Test).filter(Test.creator == current_user.id).all()
            if user_tests:
                for test in user_tests:
                    questions = session.query(Question).filter(Question.test_id == test.id).all()
                    results = session.query(Results).filter(Results.id == test.id).first()
                    for question in questions:
                        answers = session.query(Answer).filter(Answer.question_id == question.id).all()
                        for answer in answers:
                            session.delete(answer)
                        session.delete(question)
                    session.delete(results)
                    session.delete(test)
            user = session.query(User).get(current_user.id)
            session.delete(user)
            session.commit()
            return redirect('/')
        return render_template('delete_user.html', title='DegradationTests', form=form,
                               message='Неправильная почта или пароль')
    return render_template('delete_user.html', title='DegradationTests', form=form)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


# Тестовые route'ы
@app.route('/choose_type')
@login_required
def choose_type():
    return render_template('tests_types.html', title='DegradationTests')


@app.route('/choose_type/<int:test_type>', methods=['GET', 'POST'])
@login_required
def make_test(test_type):
    if test_type == 1:
        form = TestNumbersForm()
    elif test_type == 2 or test_type == 3:
        form = TestPercentForm()
    if request.method == 'POST':
        # Добавляю в БД основную информацию о тесте и получаю id для дальнейшего использования
        if test_type == 1:
            test_title = f'Какой вы {form.test_title.data}?'
        elif test_type == 2:
            test_title = f'На сколько ты совместим с {form.test_title.data}?'
        elif test_type == 3:
            test_title = f'Насколько вы {form.test_title.data}?'
        test_id = post('http://127.0.0.1:8080/api/tests', json={
            'type': test_type,
            'creator': current_user.id,
            'title': test_title,
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
                'position': 1,
                'text': question.answer_1.data,
                'result': question.choose_num_1.data if test_type == 1 else question.choose_per_1.data
            })

            post('http://127.0.0.1:8080/api/answers', json={
                'question_id': question_id,
                'position': 2,
                'text': question.answer_2.data,
                'result': question.choose_num_2.data if test_type == 1 else question.choose_per_2.data
            })

            post('http://127.0.0.1:8080/api/answers', json={
                'question_id': question_id,
                'position': 3,
                'text': question.answer_3.data,
                'result': question.choose_num_3.data if test_type == 1 else question.choose_per_3.data
            })

            post('http://127.0.0.1:8080/api/answers', json={
                'question_id': question_id,
                'position': 4,
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
        return render_template('create_test_t1.html', title='DegradationTests', form=form)
    elif test_type == 2:
        return render_template('create_test_t2.html', title='DegradationTests', form=form)
    elif test_type == 3:
        return render_template('create_test_t3.html', title='DegradationTests', form=form)


@app.route('/test_edit/<int:test_id>', methods=['GET', 'POST'])
@login_required
def edit_test(test_id):
    if request.method == 'GET':
        session = db_session.create_session()
        test = session.query(Test).filter(Test.id == test_id).first()
        if test and (current_user.id == test.creator or current_user.id == 1):
            if test.type == 1:
                form = TestNumbersForm()
                # Заполняю основную информацию о тесте
                form.test_title.data = test.title[9:].replace('?', '')
                form.test_description.data = test.description
                form.privacy.data = test.status
                # Заполняю информацию о вопросах и ответах
                questions = session.query(Question).filter(Question.test_id == test.id).all()
                for question, form_question in zip(questions, form.questions):
                    form_question.title.data = question.text
                    answers = session.query(Answer).filter(Answer.question_id == question.id).all()
                    for answer in answers:
                        if answer.position == 1:
                            form_question.answer_1.data = answer.text
                            form_question.choose_num_1.data = str(answer.result)
                        elif answer.position == 2:
                            form_question.answer_2.data = answer.text
                            form_question.choose_num_2.data = str(answer.result)
                        elif answer.position == 3:
                            form_question.answer_3.data = answer.text
                            form_question.choose_num_3.data = str(answer.result)
                        else:
                            form_question.answer_4.data = answer.text
                            form_question.choose_num_4.data = str(answer.result)
                # Заполняю информацию о результатах
                results = session.query(Results).filter(Results.id == test.id).first()
                form.result_num_1.data = results.comment_1
                form.result_num_2.data = results.comment_2
                form.result_num_3.data = results.comment_3
                form.result_num_4.data = results.comment_4
            elif test.type == 2 or test.type == 3:
                form = TestPercentForm()
                # Заполняю основную информацию о тесте
                if test.type == 2:
                    form.test_title.data = test.title[26:].replace('?', '')
                elif test.type == 3:
                    form.test_title.data = test.title[13:].replace('?', '')
                form.test_description.data = test.description
                form.privacy.data = test.status
                # Заполняю информацию о вопросах и ответах
                questions = session.query(Question).filter(Question.test_id == test.id).all()
                for question, form_question in zip(questions, form.questions):
                    form_question.title.data = question.text
                    answers = session.query(Answer).filter(Answer.question_id == question.id).all()
                    for answer in answers:
                        if answer.position == 1:
                            form_question.answer_1.data = answer.text
                            form_question.choose_per_1.data = str(answer.result)
                        elif answer.position == 2:
                            form_question.answer_2.data = answer.text
                            form_question.choose_per_2.data = str(answer.result)
                        elif answer.position == 3:
                            form_question.answer_3.data = answer.text
                            form_question.choose_per_3.data = str(answer.result)
                        else:
                            form_question.answer_4.data = answer.text
                            form_question.choose_per_4.data = str(answer.result)
                # Заполняю информацию о результатах
                results = session.query(Results).filter(Results.id == test.id).first()
                form.result_per_1.data = results.comment_1
                form.result_per_2.data = results.comment_2
                form.result_per_3.data = results.comment_3
                form.result_per_4.data = results.comment_4
        else:
            abort(404)
    if request.method == 'POST':
        session = db_session.create_session()
        test = session.query(Test).filter(Test.id == test_id).first()
        if test and (current_user.id == test.creator or current_user.id == 1):
            # Заполняю основную информацию о тесте
            if test.type == 1:
                form = TestNumbersForm()
                test.title = f'Какой вы {form.test_title.data}?'
            elif test.type == 2:
                form = TestPercentForm()
                test.title = f'На сколько ты совместим с {form.test_title.data}?'
            elif test.type == 3:
                form = TestPercentForm()
                test.title = f'Насколько вы {form.test_title.data}?'
            test.description = form.test_description.data
            test.status = form.privacy.data
            # Заполняю информацию о вопросах теста
            questions = session.query(Question).filter(Question.test_id == test.id).all()
            for question, form_question in zip(questions, form.questions):
                form_question.title.data = question.text
                answers = session.query(Answer).filter(Answer.question_id == question.id).all()
                for answer in answers:
                    if test.type == 1:
                        if answer.position == 1:
                            answer.text = form_question.answer_1.data
                            answer.result = form_question.choose_num_1.data
                        elif answer.position == 2:
                            answer.text = form_question.answer_2.data
                            answer.result = form_question.choose_num_2.data
                        elif answer.position == 3:
                            answer.text = form_question.answer_3.data
                            answer.result = form_question.choose_num_3.data
                        else:
                            answer.text = form_question.answer_4.data
                            answer.result = form_question.choose_num_4.data
                    elif test.type == 2 or test.type == 3:
                        if answer.position == 1:
                            answer.text = form_question.answer_1.data
                            answer.result = form_question.choose_per_1.data
                        elif answer.position == 2:
                            answer.text = form_question.answer_2.data
                            answer.result = form_question.choose_per_2.data
                        elif answer.position == 3:
                            answer.text = form_question.answer_3.data
                            answer.result = form_question.choose_per_3.data
                        else:
                            answer.text = form_question.answer_4.data
                            answer.result = form_question.choose_per_4.data
            results = session.query(Results).filter(Results.id == test.id).first()
            if test.type == 1:
                results.comment_1 = form.result_num_1.data
                results.comment_2 = form.result_num_2.data
                results.comment_3 = form.result_num_3.data
                results.comment_4 = form.result_num_4.data
            elif test.type == 2 or test.type == 3:
                results.comment_1 = form.result_per_1.data
                results.comment_2 = form.result_per_2.data
                results.comment_3 = form.result_per_3.data
                results.comment_4 = form.result_per_4.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    if test.type == 1:
        return render_template('create_test_t1.html', title='DegradationTests', form=form, editing=True, test_id=test_id)
    elif test.type == 2:
        return render_template('create_test_t2.html', title='DegradationTests', form=form, editing=True, test_id=test_id)
    elif test.type == 3:
        return render_template('create_test_t3.html', title='DegradationTests', form=form, editing=True, test_id=test_id)


@app.route('/test_delete/<int:test_id>', methods=['GET', 'POST'])
@login_required
def delete_test(test_id):
    session = db_session.create_session()
    test = session.query(Test).filter(Test.id == test_id).first()
    if test and (current_user.id == test.creator or current_user.id == 1):
        questions = session.query(Question).filter(Question.test_id == test.id).all()
        results = session.query(Results).filter(Results.id == test.id).first()
        for question in questions:
            answers = session.query(Answer).filter(Answer.question_id == question.id).all()
            for answer in answers:
                session.delete(answer)
            session.delete(question)
        session.delete(results)
        session.delete(test)
        session.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/test_solve/<int:test_id>', methods=['GET', 'POST'])
@login_required
def solve_test(test_id):
    form = TestPassingForm()
    session = db_session.create_session()
    test = session.query(Test).filter(Test.id == test_id).first()
    if request.method == 'GET':
        if test:
            questions = session.query(Question).filter(Question.test_id == test.id).all()
            for question, variant in zip(questions, form.variants):
                answers = session.query(Answer).filter(Answer.question_id == question.id).all()
                variant.answer_variants.label = question.text
                variant.answer_variants.choices = [(str(answer.result), answer.text) for answer in answers]
        else:
            abort(404)
    if request.method == 'POST':
        session = db_session.create_session()
        test = session.query(Test).filter(Test.id == test_id).first()
        if test:
            count_result = []
            result = [0, 0]
            for variant in form.variants:
                count_result.append(int(variant.answer_variants.data))
            if test.type == 1:
                for i in count_result:
                    if count_result.count(i) > result[1]:
                        result = [i , count_result.count(i)]
                result = result[0]
            if test.type == 2 or test.type == 3:
                result = sum(count_result)
            return redirect(f'/test_result/{test.id}/{result}')
        else:
            abort(404)
    return render_template('solve_test.html', title='DegradationTests', form=form, test=test)


@app.route('/test_result/<int:test_id>/<int:result>')
@login_required
def result_test(test_id, result):
    session = db_session.create_session()
    test = session.query(Test).filter(Test.id == test_id).first()
    if test:
        results = session.query(Results).filter(Results.id == test_id).first()
        if test.type == 1:
            result_message = 'Поздравляем! Вы '
        elif test.type == 2:
            result_message = f"Вы совместимы с {test.title[26:].replace('?', '')} на {result}%! "
        elif test.type == 3:
            result_message = f"Вы {test.title[13:].replace('?', '')} на {result}%! "
        if result == 1 or 0 <= result <= 25:
            result_message += results.comment_1
        elif result == 2 or 0 <= result <= 25:
            result_message += results.comment_2
        elif result == 3 or 51 <= result <= 75:
            result_message += results.comment_3
        elif result == 4 or 76 <= result <= 100:
            result_message += results.comment_4
    else:
        abort(404)
    return render_template('result_test.html', title='DegradationTests', result_message=result_message, test_id=test_id)


if __name__ == '__main__':
    main()
