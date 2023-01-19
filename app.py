import os
import secrets
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from peewee import MySQLDatabase, Model, IntegerField, DoubleField, TextField, ForeignKeyField, DateTimeField, \
    PrimaryKeyField

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ['SECRET_KEY']
app.config["JWT_ERROR_MESSAGE_KEY"] = 'message'

CORS(app)
database = MySQLDatabase(os.environ['DATABASE_NAME'], user=os.environ['DATABASE_USER'], password=os.environ['DATABASE_PASS'], host=os.environ['DATABASE_HOST'], port=int(os.environ['DATABASE_PORT']))
jwt = JWTManager(app)


class Setting(Model):
    id = PrimaryKeyField()
    key = TextField(unique=True)
    value = TextField()

    class Meta:
        database = database


class Account(Model):
    id = PrimaryKeyField()
    card_number = IntegerField(unique=True)
    name = TextField()
    balance = DoubleField()

    class Meta:
        database = database


class Stock(Model):
    id = PrimaryKeyField()
    code = TextField(unique=True)
    full_name = TextField()
    total_available = IntegerField()

    def get_current_price(self):
        prices = self.prices.order_by(StockPrice.datetime.desc())

        if prices.exists():
            return prices.get().price

        return 0

    class Meta:
        database = database


class StockPrice(Model):
    id = PrimaryKeyField()
    stock = ForeignKeyField(Stock, backref='prices', on_delete='CASCADE')
    price = DoubleField()
    datetime = DateTimeField()

    class Meta:
        database = database


class Purchase(Model):
    id = PrimaryKeyField()
    account = ForeignKeyField(Account, backref='purchases', on_delete='CASCADE')
    stock = ForeignKeyField(Stock, backref='purchases', on_delete='CASCADE')
    price = DoubleField()
    datetime = DateTimeField()

    class Meta:
        database = database


class Event(Model):
    id = PrimaryKeyField()
    title = TextField()
    body = TextField()

    class Meta:
        database = database


class Tag(Model):
    id = PrimaryKeyField()
    name = TextField(unique=True)

    class Meta:
        database = database


class StockTag(Model):
    id = PrimaryKeyField()
    tag = ForeignKeyField(Tag, backref='stocks', on_delete='CASCADE')
    stock = ForeignKeyField(Stock, backref='tags', on_delete='CASCADE')

    class Meta:
        database = database


class EventTag(Model):
    id = PrimaryKeyField()
    tag = ForeignKeyField(Tag, backref='events', on_delete='CASCADE')
    event = ForeignKeyField(Event, backref='tags', on_delete='CASCADE')

    class Meta:
        database = database


class Placeholder(Model):
    id = PrimaryKeyField()
    name = TextField(unique=True)

    class Meta:
        database = database


class PlaceholderValue(Model):
    id = PrimaryKeyField()
    placeholder = ForeignKeyField(Placeholder, backref='values', on_delete='CASCADE')
    value = TextField()

    class Meta:
        database = database


@app.route('/')
def hello_world():
    return jsonify({
        'message': 'Hello!'
    }), 200


@app.post('/auth')
def auth():
    password = request.json.get('admin_password', None)

    if password == os.environ['ADMIN_PASSWORD']:
        return jsonify({
            'token': create_access_token(identity=secrets.token_hex()),
        }), 200

    return jsonify({
        'message': 'Password incorrect or not supplied.',
    }), 401


@app.get('/account')
@app.get('/account/<card_number>')
def get_accounts(card_number=None):
    response = {}

    if card_number is not None:
        account = Account.get_or_none(card_number=card_number)

        if account is not None:
            response = format_account_json(account)
        else:
            return jsonify({
                'message': 'Account not found.'
            }), 404
    else:
        for account in Account.select():
            response.update(format_account_json(account))

    return jsonify(response), 200


@app.put('/account')
@jwt_required()
def put_account():
    card_number = request.json.get('cardNumber', None)
    name = request.json.get('name', None)

    if card_number is None or name is None:
        return jsonify({
            'message': 'Missing cardNumber and/or name of account.'
        }), 400

    account = Account.get_or_none(card_number=card_number)

    if account is None:
        account = Account.create(card_number=card_number, name=name)
    else:
        account.name = name

    account.save()

    return jsonify({
        'message': 'Account updated!'
    }), 200


def format_account_json(account):
    return {
        account.card_number: {
            'name': account.name,
            'balance': account.balance
        }
    }


@app.delete('/account/<card_number>')
@jwt_required()
def delete_account(card_number):
    account = Account.get_or_none(card_number=card_number)

    if account is not None:
        account.delete_instance()

        return jsonify({
            'message': 'Account deleted.'
        }), 200
    else:
        return jsonify({
            'message': 'Account not found.'
        }), 404


@app.put('/stock')
@jwt_required()
def put_stock():
    code = request.json.get('code', None)
    full_name = request.json.get('fullName', None)
    price = request.json.get('currentPrice', None)
    tags = request.json.get('tags', None)

    if code is None or full_name is None or price is None:
        return jsonify({
            'message': 'code, full_name and price are required.'
        }), 400

    stock = Stock.get_or_none(code=code)

    if stock is None:
        stock = Stock.create(code=code, full_name=full_name)
    else:
        stock.full_name = full_name

    stock.save()

    if tags is not None:
        for tag in get_tags(tags.split(',')):
            stock_tag = StockTag.create(tag=tag, stock=stock)
            stock_tag.save()

    stock_price = StockPrice.create(stock=stock, price=price, datetime=datetime.now())
    stock_price.save()

    return jsonify({
        'message': 'OK'
    }), 200


def get_tags(tags):
    tags = [tag.strip().lower() for tag in tags]
    records = []

    for tag in tags:
        record = Tag.get_or_none(name=tag)

        if record is None:
            record = Tag.create(name=tag)

        records.append(record)

    return records


@app.get('/stock')
@app.get('/stock/<stock_code>')
def get_stocks(stock_code=None):
    response = {}

    if stock_code is not None:
        stock = Stock.get_or_none(code=stock_code)

        if stock is not None:
            response = format_stock_json(stock)
        else:
            return jsonify({
                'message': 'Stock not found.'
            }), 404
    else:
        for stock in Stock.select():
            response.update(format_stock_json(stock))

    return jsonify(response), 200


def format_stock_json(stock):
    return {
        stock.code: {
            'fullName': stock.full_name,
            'currentPrice': stock.get_current_price(),
            'pctChange': 0 if stock.code == 'XYZ' else (-1 if stock.code == 'ABC' else 1),
            'tags': [stock_tag.tag.name for stock_tag in stock.tags],
        }
    }


@app.delete('/stock/<stock_code>')
@jwt_required()
def delete_stock(stock_code):
    stock = Stock.get_or_none(code=stock_code)

    if stock is not None:
        stock.delete_instance()

        return jsonify({
            'message': 'Stock deleted.'
        }), 200
    else:
        return jsonify({
            'message': 'Stock not found.'
        }), 404


@app.post('/purchase')
@jwt_required()
def put_purchase():
    account_id = request.json.get('account', None)
    stock_code = request.json.get('stock', None)

    if account_id is None or stock_code is None:
        return jsonify({
            'message': 'account and stock are required.'
        }), 400

    account = Account.get_or_none(card_number=account_id)
    stock = Stock.get_or_none(code=stock_code)

    if account is None or stock is None:
        return jsonify({
            'message': 'account or stock does not exist.'
        }), 400

    stock_price = stock.get_current_price()

    purchase = Purchase.create(account=account, stock=stock, datetime=datetime.now(), price=stock_price)
    purchase.save()

    account.balance -= stock_price
    account.save()

    return jsonify({
        'message': 'OK'
    }), 200


@app.get('/event')
@app.get('/event/<card_number>')
def get_events(event_id=None):
    response = {}

    if event_id is not None:
        event = Account.get_or_none(id=event_id)

        if event is not None:
            response = format_event_json(event)
        else:
            return jsonify({
                'message': 'Event not found.'
            }), 404
    else:
        for event in Event.select():
            response.update(format_event_json(event))

    return jsonify(response), 200


@app.post('/event')
@jwt_required()
def put_event():
    title = request.json.get('title', None)
    body = request.json.get('body', None)
    tags = request.json.get('tags', None)

    if title is None or body is None:
        return jsonify({
            'message': 'Missing name and/or body of event.'
        }), 400

    event = Event.create(title=title, body=body)
    event.save()

    if tags is not None:
        for tag in get_tags(tags.split(',')):
            stock_tag = EventTag.create(tag=tag, event=event)
            stock_tag.save()

    return jsonify({
        'message': 'Account updated!'
    }), 200


def format_event_json(event):
    return {
        event.id: {
            'id': event.id,
            'title': event.title,
            'body': event.body,
            'tags': [event_tag.tag.name for event_tag in event.tags]
        }
    }


@app.delete('/event/<event_id>')
@jwt_required()
def delete_event(event_id):
    event = Event.get_or_none(id=event_id)

    if event is not None:
        event.delete_instance()

        return jsonify({
            'message': 'Account deleted.'
        }), 200
    else:
        return jsonify({
            'message': 'Account not found.'
        }), 404


@app.get('/placeholder')
@app.get('/placeholder/<placeholder_name>')
def get_placeholders(placeholder_name=None):
    response = {}

    if placeholder_name is not None:
        placeholder = Placeholder.get_or_none(name=placeholder_name)

        if placeholder is not None:
            response = format_placeholder_json(placeholder)
        else:
            return jsonify({
                'message': 'Placeholder not found.'
            }), 404
    else:
        for placeholder in Placeholder.select():
            response.update(format_placeholder_json(placeholder))

    return jsonify(response), 200


@app.put('/placeholder')
@jwt_required()
def put_placeholder():
    name = request.json.get('name', None)
    values = request.json.get('values', None)

    if name is None or values is None:
        return jsonify({
            'message': 'name and values are required.'
        }), 400

    placeholder = Placeholder.get_or_none(name=name)

    if placeholder is None:
        placeholder = Placeholder.create(name=name)

    placeholder.save()

    for value in [value.strip() for value in values.split(',')]:
        placeholder_value = PlaceholderValue.create(placeholder=placeholder, value=value)
        placeholder_value.save()

    return jsonify({
        'message': 'OK'
    }), 200


def format_placeholder_json(placeholder):
    return {
        placeholder.name: {
            'values': [placeholder_value.value for placeholder_value in placeholder.values]
        }
    }


@app.delete('/placeholder/<placeholder_name>')
@jwt_required()
def delete_placeholder(placeholder_name):
    placeholder = Placeholder.get_or_none(name=placeholder_name)

    if placeholder is not None:
        placeholder.delete_instance()

        return jsonify({
            'message': 'Account deleted.'
        }), 200
    else:
        return jsonify({
            'message': 'Account not found.'
        }), 404


database.connect()
database.create_tables([Setting, Account, Stock, StockPrice, Purchase, Event, Tag, StockTag, EventTag, Placeholder, PlaceholderValue])

if __name__ == '__main__':
    app.run()
