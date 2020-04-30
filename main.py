import flask
from flask import Flask, request, redirect, render_template, jsonify
from data import db_session
from data.goods import Good
from data.carts import Cart
from data.users import User
import os
from data.Category import Category
from data.completed_cart import CompletedCart
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms.fields.html5 import EmailField
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tmas_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/pccomponents.db")


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


@app.route('/api/users', methods=['GET', 'POST'])
def get_users():
    try:
        if request.method == 'GET':
            session = db_session.create_session()
            users = session.query(User).all()
            return {
                'users':
                    [item.to_dict(only=('name', 'surname', 'is_admin'))
                     for item in users]
            }
        elif request.method == 'POST':
            if not request.json:
                return {'error': 'Empty request'}
            elif not all(key in request.json for key in
                         ['name', 'surname', 'email', 'password', 'is_admin']):
                return {'error': 'Bad request'}
            session = db_session.create_session()

            if session.query(User).filter(User.email == request.json['email']).first():
                return {'error': 'user exists'}

            user = User(
                name=request.json['name'],
                surname=request.json['surname'],
                email=request.json['email'],
                is_admin=request.json['is_admin']
            )
            user.set_password(request.json['password'])
            session.add(user)
            session.commit()
            return jsonify({'success': 'OK'})
    except Exception as e:
        return e


@app.route('/api/users/<int:user_id>', methods=['GET', 'POST'])
def get_one_user(user_id):
    if request.method == 'GET':
        session = db_session.create_session()
        users = session.query(User).filter(User.id == user_id)
        return {
            'users':
                [item.to_dict(only=('name', 'surname', 'is_admin'))
                 for item in users]
        }


@app.route('/api/goods', methods=['GET', 'POST'])
def get_goods():
    if request.method == 'GET':
        session = db_session.create_session()
        goods = session.query(Good).all()
        return {
            'goods':
                [item.to_dict(only=('id', 'Category_id', 'Producer_id', 'Good_name', 'info', 'price'))
                 for item in goods]
        }
    elif request.method == 'POST':
        if not request.json:
            return {'error': 'Empty request'}
        elif not all(key in request.json for key in
                     ['category_id', 'producer', 'name', 'info', 'price']):
            return {'error': 'Bad request'}
        session = db_session.create_session()
        good = Good(
            Good_name=request.json['name'],
            Category_id=request.json['category_id'],
            Producer_id=request.json['producer'],
            price=request.json['price'],
            info=request.json['info']
        )
        session.add(good)
        session.commit()
        return jsonify({'success': 'OK'})


@app.route('/api/cart/all')
def get_cart():
    session = db_session.create_session()
    goods = session.query(Cart).all()
    return {
        'goods':
            [item.to_dict(only=('user_id', 'producer', 'name', 'info', 'price'))
             for item in goods]
    }


@app.route('/api/completed_cart/all')
def get_completed_cart():
    session = db_session.create_session()
    goods = session.query(CompletedCart).all()
    return {
        'goods':
            [item.to_dict(only=('user_id', 'producer', 'name', 'info', 'price'))
             for item in goods]
    }


@app.route('/api/goods/one/<int:good_id>')
def get_one_good(good_id):
    session = db_session.create_session()
    goods = session.query(Good).filter(Good.id == good_id)
    return {
        'goods':
            [item.to_dict(only=('id', 'Category_id', 'Producer_id', 'Good_name', 'info', 'price'))
             for item in goods]
    }


@app.route('/api/goods/<category_id>', methods=['GET'])
def get_one_category(category_id):
    session = db_session.create_session()
    goods = session.query(Good).filter(Good.Category_id == category_id)
    return {
        'goods':
            [item.to_dict(only=('id', 'Category_id', 'Producer_id', 'Good_name', 'info', 'price'))
             for item in goods]
    }


@app.route('/catalog/<category_id>', methods=['POST', 'GET'])
def category(category_id):
    if request.method == 'GET':
        return flask.render_template("catalog.html", goods=get_one_category(category_id))
    elif request.method == 'POST':
        a = list(dict(request.form).keys())[0]
        good = get_one_good(a)['goods']
        producer = good[0]['Producer_id']
        info = good[0]['info']
        price = good[0]['price']
        name = good[0]['Good_name']
        cart = Cart(user_id=current_user.id, name=name, price=price, info=info, producer=producer)
        session = db_session.create_session()
        session.add(cart)
        session.commit()

        return flask.render_template("catalog.html", goods=get_one_category(category_id))


@app.route('/cart', methods=['POST', 'GET'])
def cart():
    if request.method == 'GET':
        if current_user.is_authenticated:
            return render_template("cart.html", username=current_user.name, goods=get_cart())
        else:
            return render_template("cart.html", username='anonymous')
    elif request.method == 'POST':

        session = db_session.create_session()
        goods_in_cart = session.query(Cart).filter(current_user.id == Cart.user_id).all()
        for good in goods_in_cart:
            session1 = db_session.create_session()
            compl_cart = CompletedCart(user_id=good.user_id, price=good.price, info=good.info, name=good.name,
                                       producer=good.producer)
            session1.add(compl_cart)
            session1.commit()
            session.delete(good)
        session.commit()

        return render_template("cart.html", username=current_user.name, goods=get_cart())


@app.route('/catalog')
def catalog():
    try:
        return flask.render_template("catalog.html", goods=get_goods())
    except Exception as e:
        return e


@app.route('/completed_cart')
def completed_cart():
    return flask.render_template("completed_cart.html", username=current_user.name, goods=get_completed_cart())


def main():
    app.run()


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)