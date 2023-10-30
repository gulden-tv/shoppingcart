import redis
import sqlite3
import json

import requests
from pymongo import MongoClient
from datetime import datetime
import pytz
import sys

r = redis.StrictRedis(
    # host='10.21.17.68',
    host='127.0.0.1',
    port=6379,
    password='please',
    charset="utf-8",
    decode_responses=True
)
# m = MongoClient('mongodb://admin:helloworld312@10.21.17.68', 27017)
# mdb = m['ShoppingCart']
connection = sqlite3.connect('index/database.sqlite3', check_same_thread=False)
connection.row_factory = sqlite3.Row # make fetch to keyname array
sql = connection.cursor()

def getCartByUserId(uid):
    cartid = 'cart-' + uid
    json_cart = r.get(cartid)
    products = getProducts()
    cart = {'total': 0.0, 'quantity': 0, 'items': []}
    if json_cart:
        cart['items'] = json.loads(json_cart)

    for product in products:
        for c in cart['items']:
            if c['product_id'] == product['id']:
                c['name'] = product['name']
                c['price'] = product['price']
                cart['total'] += float(c['price']) * float(c['quantity'])
                cart['quantity'] += int(c['quantity'])
    return cart


def putToCart(uid, productid):
    cartid = 'cart-' + uid
    json_cart = r.get(cartid)
    cart = []
    if json_cart:
        cart = json.loads(json_cart)

    in_cart = False
    for item in cart:
        if item['product_id'] == productid:
            item['quantity'] += 1
            in_cart = True
            break
    if not in_cart:
        cart.append({"product_id": productid, "quantity": 1})
    r.set(cartid, json.dumps(cart))
    r.expire(cartid, 600)  # Time life of cart in seconds


def clearCart(uid):
    cartid = 'cart-' + uid
    r.expire(cartid, 0)


def getProducts():
    sql.execute("SELECT id, name, stock, price FROM products")
    return sql.fetchall()
    # return json.loads(r.get('products'))


def makeOrder(uid, uname):
    order = getCartByUserId(uid)
    # order["username"] = uname
    IST = pytz.timezone('Asia/Shanghai')
    order["date"] = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
    # orders = mdb["orders"] # store to mongo
    # oid = orders.insert_one(order).inserted_id # store to mongo
    # r.sadd('order-' + str(uid), json.dumps(order)) # store to redis
    sql = connection.execute("""INSERT INTO orders (user_id, quantity, total, created) VALUES(?, ?, ?, ?);""", (uid, order['quantity'], order['total'], order["date"]))
    orderid = sql.lastrowid
    connection.execute("""INSERT INTO order_items (order_id, items) VALUES(?, ?);""", (orderid, json.dumps(order['items'])))
    connection.commit()
    clearCart(uid)
    return orderid # order["date"]


def getOrdersByUserId(uid):
    # orders = mdb['orders'].find({'userid': uid}) # get orders from mongodb
    # orders = r.smembers('order-' + str(uid)) # get from redis

    sql.execute("""SELECT id, quantity as numbers, total, created as date FROM orders WHERE user_id = ?;""", (uid, )) # get from sqlite3
    orders = sql.fetchall()
    return orders


def getOrderById(oid):
    sql.execute("""SELECT o.id, o.user_id, o.quantity, o.total, o.created, oi.items 
        FROM orders o, order_items oi 
        WHERE o.id = ? AND oi.order_id = ?;""", (oid, oid, ))
    rows = sql.fetchone()
    if rows is not None:
        order = dict(rows)
        order['items'] = json.loads(order['items'])
    else:
        order = {}
        order['items'] = []
    return order


def getTotalSumAllOrders(uid):
    # orders = r.smembers('order-' + str(uid)) # get from redis
    # sum = 0.0
    # for order in orders:
    #     json_order = json.loads(order)
    #     sum += float(json_order['total'])
    sql.execute("""SELECT sum(total) as sum FROM orders WHERE user_id = ?""", (uid,))
    sum = sql.fetchone()['sum']
    return sum if sum is not None else 0.0

def showMessage():
    message = requests.session['message']
    requests.session['message'] = ""
    return message


def getUserId(request=None):
    if 'user' not in request.session:
        request.session['user'] = request.session._get_or_create_session_key()
        request.session['username'] = "Undefined"
        request.session['message'] = ""
    userid = request.session['user']
    return userid

r.close()

