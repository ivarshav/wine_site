import os

import bcrypt
from flask import Flask, render_template, abort, request, redirect, url_for, session
from flask_login import LoginManager, login_required, logout_user, login_user
from sqlalchemy import desc

from connect import connect, get_engine
from models import Wines, User

app = Flask(__name__)
app.config.from_pyfile('config.py')

login_manager = LoginManager()
login_manager.init_app(app)

engine = get_engine()
db_session = connect()


@app.route('/wine/<int:wine_id>', methods=['GET'])
@login_required
def show_wine_page(wine_id):
    wine = db_session.query(Wines).get(wine_id)
    if wine is None:
        abort(404, 'Error: wine {wine_id} does not exists'.format(wine_id=wine_id))

    return render_template('wine.j2', results=[wine.to_dict()], title="Wine #{wine_id}".format(wine_id=wine_id))


@app.route('/wines', methods=['POST'])
@login_required
def search_wines():
    variety, points, price, country, winery = request.form.get('variety'), request.form.get('points'), request.form.get(
        'price'), request.form.get('country'), request.form.get('winery')

    wines = db_session.query(Wines)

    if variety:
        wines = wines.filter_by(variety=variety)
    if points:
        wines = wines.filter_by(points=points)
    if price:
        wines = wines.filter_by(price=price)
    if country:
        wines = wines.filter_by(country=country)
    if winery:
        wines = wines.filter_by(winery=winery)
    wines = wines.order_by(desc(Wines.points))
    res = []
    for wine in wines:
        res.append(wine.to_dict())
    if not res:
        return render_template('index.j2', response="No results found")
    return render_template('wine.j2', results=res, title="Wines")


@app.route('/cart', methods=['GET'])
@login_required
def view_cart():
    user_id = session.get("_user_id")
    user = db_session.query(User).get(user_id)

    wines = db_session.query(Wines).join((User, Wines.users)).filter(Wines.users.any(User.id == user_id)).order_by(
        desc(Wines.points)).all()
    res = []
    pay = 0
    for wine in wines:
        res.append(wine.to_dict())
        pay += wine.price
    return render_template('cart.j2', results=res, pay=pay, title="Cart - {username}".format(username=user.username))


@app.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    wine_id = request.form.get('wine_id')
    wine = db_session.query(Wines).get(wine_id)

    user_id = session.get("_user_id")
    user = db_session.query(User).get(user_id)
    wine.users.append(user)

    db_session.add(wine)
    db_session.flush()
    db_session.commit()
    db_session.refresh(wine)
    return redirect(url_for('view_cart'))


@login_required
@app.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    wine_id = request.form.get('wine_id')
    user_id = session.get("_user_id")

    user = db_session.query(User).get(user_id)
    wine = user.wines.filter_by(id=wine_id).first()

    user.wines.remove(wine)
    db_session.flush()
    db_session.commit()
    return redirect(url_for('view_cart'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.j2')

    username = request.form.get('username')
    if username is None:
        return abort(400, 'No username supplied')
    user = db_session.query(User).filter_by(username=username).first()
    if user:
        return abort(403, 'Username {username} is already exists'.format(username=username))

    salt = bcrypt.gensalt(prefix=b'2b', rounds=10)
    unhashed_password = request.form['password'].encode('utf-8')
    hashed_password = bcrypt.hashpw(unhashed_password, salt)
    user = User.create(db_session, password=hashed_password, name=request.form.get('name'),
                       username=username,
                       email=request.form.get('email'))
    return 'User {} was successfully created!!'.format(user.username)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('login.j2')
    username = request.form.get('username')
    if username is None:
        return abort(400, 'No username supplied')
    user = db_session.query(User).filter_by(username=username).first()
    if not user:
        return abort(403, 'Username {username} does not exist'.format(username=username))

    password = request.form['password'].encode('utf-8')
    real_password = str(user.password).encode('utf-8')

    if not bcrypt.checkpw(password, real_password):
        return abort(403, 'Username and password does not match')

    login_user(user, remember=True)
    return redirect(url_for('hello_world'))


@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).get(user_id)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('hello_world'))


@app.route("/")
def hello_world():
    return render_template('index.j2')


if __name__ == "__main__":
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.run(threaded=True, port=5000)
