import redis
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
m = MongoClient('mongodb://admin:helloworld312@10.21.17.68', 27017)
mdb = m['ShoppingCart']

def getCartByUserId(uid):
    cartid = 'cart-' + uid
    json_cart = r.get(cartid)
    json_products = r.get('products')
    products = json.loads(json_products)
    cart = {'total': 0.0, 'items': []}
    if json_cart:
        cart['items'] = json.loads(json_cart)

    for product in products:
        for c in cart['items']:
            if c['product_id'] == product['id']:
                c['name'] = product['name']
                c['price'] = product['price']
                cart['total'] += float(c['price']) * float(c['quantity'])
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
    return json.loads(r.get('products'))


def makeOrder(uid, uname):
    order = getCartByUserId(uid)
    order["username"] = uname
    IST = pytz.timezone('Asia/Shanghai')
    order["date"] = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
    # orders = mdb["orders"] # store to mongo
    # oid = orders.insert_one(order).inserted_id # store to mongo
    r.sadd('order-' + str(uid), json.dumps(order)) # store to redis
    clearCart(uid)
    return order["date"]


def getOrdersByUserId(uid):
    # orders = mdb['orders'].find({'userid': uid}) # get orders from mongodb
    orders = r.smembers('order-' + str(uid)) # get from redis
    ret = []
    for order in orders:
        ret.append(json.loads(order))
    return ret


def showMessage():
    message = requests.session['message']
    requests.session['message'] = ""
    return message


r.close()
