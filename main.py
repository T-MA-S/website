from flask import Flask, request, redirect, render_template
from data import db_session
from data.goods import Good
from data.carts import Cart
from data.users import User
from data.Category import Category
import shop_api
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm

from wtforms.fields.html5 import EmailField
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tmas_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


class RegisterForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    surname = StringField('Фамилия пользователя', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    is_admin = StringField('Введите промокод(для администраторов)')
    submit = SubmitField('Войти')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if form.is_admin.data == 'admin':
            a = 1
        else:
            a = 0
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            is_admin=a
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/authorization')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/authorization', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('authorization.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('authorization.html', title='Авторизация', form=form)


@app.route('/service', methods=['GET', 'POST'])
def service():
    if request.method == 'GET':
        return render_template("service.html")
    elif request.method == 'POST':
        return redirect('/')


@app.route('/help')
def help():
    return render_template("help.html")


@app.route('/')
def homepage():
    return render_template("homepage.html")


@app.route('/add_to_db_form', methods=['POST', 'GET'])
def add_to_db_form():
    if request.method == 'GET':
        return render_template("add_to_db_form.html")
    elif request.method == 'POST':
        db_session.global_init("db/blogs.sqlite")

        good = Good()
        good.Category_id = request.form['category']
        good.Producer_id = request.form['producer']
        good.Good_name = request.form['name']
        good.info = request.form['info']
        good.price = request.form['price']
        session = db_session.create_session()
        session.add(good)
        session.commit()

        return redirect('/cart')


def main():
    db_session.global_init("db/pccomponents.db")

    app.register_blueprint(shop_api.blueprint)
    app.run()


if __name__ == '__main__':
    main()
