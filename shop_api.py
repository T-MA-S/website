import flask
import json
from flask_login import current_user
import requests
from data.users import User
from flask import jsonify, make_response, request, redirect, render_template, abort
from data import db_session
from data.carts import Cart
from data.goods import Good
from data.completed_cart import CompletedCart
import time

blueprint = flask.Blueprint('shop_api', __name__,
                            template_folder='templates')

producers = {'1': 'Intel', '2': 'AMD', '3': 'Gigabyte', '4': 'Asus', '5': 'MSI', '6': 'Crucial', '7': 'Kingston',
             '8': 'Goodram', '9': 'Be Quiet', '10': 'Cooler Master', '11': 'FSP', '12': 'Western Digital',
             '13': 'Seagate', '14': 'Toshiba'}


@blueprint.route('/api/users', methods=['GET', 'POST'])
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


@blueprint.route('/api/users/<int:user_id>', methods=['GET', 'POST'])
def get_one_user(user_id):
    if request.method == 'GET':
        session = db_session.create_session()
        users = session.query(User).filter(User.id == user_id)
        return {
            'users':
                [item.to_dict(only=('name', 'surname', 'is_admin'))
                 for item in users]
        }


@blueprint.route('/api/goods', methods=['GET', 'POST'])
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


@blueprint.route('/api/cart/all')
def get_cart():
    session = db_session.create_session()
    goods = session.query(Cart).all()
    return {
        'goods':
            [item.to_dict(only=('user_id', 'producer', 'name', 'info', 'price'))
             for item in goods]
    }


@blueprint.route('/api/completed_cart/all')
def get_completed_cart():
    session = db_session.create_session()
    goods = session.query(CompletedCart).all()
    return {
        'goods':
            [item.to_dict(only=('user_id', 'producer', 'name', 'info', 'price'))
             for item in goods]
    }


@blueprint.route('/api/goods/one/<int:good_id>')
def get_one_good(good_id):
    session = db_session.create_session()
    goods = session.query(Good).filter(Good.id == good_id)
    return {
        'goods':
            [item.to_dict(only=('id', 'Category_id', 'Producer_id', 'Good_name', 'info', 'price'))
             for item in goods]
    }


@blueprint.route('/api/goods/<category_id>', methods=['GET'])
def get_one_category(category_id):
    session = db_session.create_session()
    goods = session.query(Good).filter(Good.Category_id == category_id)
    return {
        'goods':
            [item.to_dict(only=('id', 'Category_id', 'Producer_id', 'Good_name', 'info', 'price'))
             for item in goods]
    }


@blueprint.route('/catalog/<category_id>', methods=['POST', 'GET'])
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


@blueprint.route('/cart', methods=['POST', 'GET'])
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


@blueprint.route('/catalog')
def catalog():
    return flask.render_template("catalog.html", goods=get_goods())


@blueprint.route('/completed_cart')
def completed_cart():
    return flask.render_template("completed_cart.html", username=current_user.name, goods=get_completed_cart())
