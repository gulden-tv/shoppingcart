import redis
import sqlite3
import json

import requests
from pymongo import MongoClient
from datetime import datetime
import pytz
import sys

# r = redis.StrictRedis(
#     # host='10.21.17.68',
#     host='127.0.0.1',
#     port=6379,
#     password='please',
#     charset="utf-8",
#     decode_responses=True
# )

connection = sqlite3.connect('index/database.sqlite3', check_same_thread=False)
connection.row_factory = sqlite3.Row # make fetch to keyname array
sql = connection.cursor()


def getCartByUserSessionSql(user_session):
    sql.execute("""SELECT product_id, name, price, count(*) as quantity,  
                (SELECT sum(products.price) FROM cart
                    LEFT JOIN products ON product_id = products.id
                    WHERE user_session = ?) as total
                FROM cart 
                LEFT JOIN products ON products.id = cart.product_id 
                WHERE user_session = ?
                GROUP BY product_id ORDER BY created""", [user_session, user_session])
    rows = sql.fetchall()
    items = [dict(row) for row in rows]
    total = items[0]['total'] if len(items) > 0 else 0
    quantity = 0
    for i in items:
        quantity += i['quantity']
    cart = {'total': total, 'quantity': quantity, 'items': items}
    # print(cart, file=sys.stderr)
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


def putToCartSql(user_session, pid):
    IST = pytz.timezone('Asia/Shanghai')
    now = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
    sql.execute("INSERT INTO cart (user_session, product_id, created) VALUES (?, ?, ?)", [user_session, pid, now])
    connection.commit()


def clearCart(user_session):
    sql.execute("DELETE FROM cart WHERE user_session = ?", [user_session])
    connection.commit()


def getProducts(pagenumber=-1):
    pagesize = 10
    if pagenumber == -1:
        sql.execute("SELECT id, name, stock, price FROM products")
    else:
        sql.execute("SELECT id, name, stock, price FROM products LIMIT ?, ?", [int(pagenumber)*pagesize, pagesize])
    return sql.fetchall()


def getProductPagesTotal(pagesize=10):
    sql.execute("SELECT count(*)/? FROM products", [int(pagesize)])
    last_page = int(sql.fetchone()[0])
    if last_page % pagesize != 0:
        last_page += 1
    return range(last_page)

def makeOrder(uid, user_session):
    order = getCartByUserSessionSql(user_session)
    IST = pytz.timezone('Asia/Shanghai')
    order["date"] = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
    sql = connection.execute("""INSERT INTO orders (user_id, quantity, total, created) VALUES(?, ?, ?, ?);""", (uid, order['quantity'], order['total'], order["date"]))
    order_id = sql.lastrowid
    connection.execute("""INSERT INTO order_items (order_id, items) VALUES(?, ?);""", (order_id, json.dumps(order['items'])))
    connection.commit()
    clearCart(user_session)
    return order_id # order["date"]


def getOrdersByUserId(uid):
    # orders = mdb['orders'].find({'userid': uid}) # get orders from mongodb
    # orders = r.smembers('order-' + str(uid)) # get from redis
    sql.execute("""SELECT id, quantity, total, created as date FROM orders WHERE user_id = ?;""", [uid]) # get from sqlite3
    orders = sql.fetchall()
    return orders


def getOrderById(oid, uid):
    sql.execute("""SELECT o.id, o.user_id, o.quantity, o.total, o.created, oi.items 
        FROM orders o, order_items oi 
        WHERE o.id = ? AND oi.order_id = ? AND o.user_id = ?;""", (oid, oid, uid))
    rows = sql.fetchone()
    if rows is not None:
        order = dict(rows)
        order['items'] = json.loads(order['items'])
    else:
        order = {}
        order['items'] = []
    return order


def getTotalSumAllOrders(uid):
    sql.execute("""SELECT sum(total) as sum FROM orders WHERE user_id = ?""", (uid,))
    sum = sql.fetchone()['sum']
    return sum if sum is not None else 0.0

def showMessage(request):
    message = request.session['message']
    request.session['message'] = {"text": "", "message_type": ""}
    return message


def setMessage(request, message, message_type="success"):
    request.session["message"] = {"text": message, "message_type": message_type}


def getUserSessionId(request=None):
    if 'user' not in request.session:
        request.session['user'] = request.session._get_or_create_session_key()
        request.session['username'] = "Undefined"
        request.session['message'] = ""
        request.session['uid'] = 0
    user_session_id = request.session['user']
    return user_session_id


def getUserId(request):
    getUserSessionId(request)
    user_id = request.session['uid'] if 'uid' in request.session else 0
    return user_id


def getUserName(uid):
    sql.execute("SELECT name FROM users WHERE id = ?;", [uid])
    name = sql.fetchone()
    return name[0] if name else "Undefined"


def checkLoginPassword(login, password):
    sql.execute("SELECT id FROM users WHERE login = ? AND password = ?;", [login, password])
    uid = sql.fetchone()
    return uid[0] if uid else 0


def loginUser(request, uid):
    if 'user' in request.session:
        request.session['uid'] = uid
    else:
        getUserSessionId(request)
        request.session['uid'] = uid
    IST = pytz.timezone('Asia/Shanghai')
    now = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')
    connection.execute("INSERT INTO lastlogin VALUES(?, ?, ?);""", [uid, now, ""])
    connection.execute("UPDATE users SET lastlogin = ? WHERE id = ?;""", [now, uid])
    connection.commit()


def getLastLoginDate(uid):
    sql.execute("SELECT date_time FROM lastlogin WHERE user_id = ? ORDER BY date_time DESC LIMIT 1, 1;", [uid])
    lastlogin = sql.fetchone()
    return lastlogin[0] if lastlogin else "Undefined"


def getUserLogin(uid):
    sql.execute("SELECT login FROM users WHERE id = ?;", [uid])
    login = sql.fetchone()
    return login[0] if login else "Undefined"


def logoutUser(request):
    if 'user' in request.session:
        request.session.delete('user')
    else:
        getUserSessionId(request)
        request.session['uid'] = 0

# r.close()

