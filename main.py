from flask import Flask, render_template, redirect, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api
from requests import get, post, delete
from data import db_session, user_resources
from forms.user_forms import RegisterForm, LoginForm, DeleteForm
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

    db_session.global_init('db/degradation_tests.db')
    app.run(port=8080)


@app.route('/')
def index():
    return render_template('base.html', title='DegradationTests')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form, message="Такая почта уже занята")
        user_id = post('http://127.0.0.1:8080/api/users', json={
            'name': form.name.data,
            'email': form.email.data,
            'password': form.password.data
        }).json()['id']
        login_user(db_sess.query(User).filter(User.id == user_id).first(), remember=True)
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
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
        if current_user.email == form.email.data and current_user.check_password(form.password.data):
            delete(f'http://127.0.0.1:8080/api/users/{current_user.id}')
            return redirect('/')
        return render_template('delete_user.html', title='Удаление', form=form, message='Неправильная почта или пароль')
    return render_template('delete_user.html', title='Удаление', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


if __name__ == '__main__':
    main()