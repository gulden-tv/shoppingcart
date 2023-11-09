from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
import requests
import redis
import json
import sys
import os
from .application import *


# r = redis.StrictRedis(
#     # host='10.21.17.68',
#     host='127.0.0.1',
#     port=6379,
#     password='please',
#     charset="utf-8",
#     decode_responses=True
# )

# Data products example
# products_backup = [
#     {
#         "id": "e182115a-63d2-42ce-8fe0-5f696ecdfba6",
#         "name": "Brilliant Watch",
#         "price": "250.00",
#         "stock": 2
#     },
#     {
#         "id": "f9a6d214-1c38-47ab-a61c-c99a59438b12",
#         "name": "Old fashion cellphone",
#         "price": "24.00",
#         "stock": 2
#     },
#     {
#         "id": "1f1321bb-0542-45d0-9601-2a3d007d5842",
#         "name": "Modern iPhone",
#         "price": "1000.00",
#         "stock": 2
#     },
#     {
#         "id": "f5384efc-eadb-4d7b-a131-36516269c218",
#         "name": "Beautiful Sunglasses",
#         "price": "12.00",
#         "stock": 2
#     },
#     {
#         "id": "6d6ca89d-fbc2-4fc2-93d0-6ee46ae97345",
#         "name": "Stylish Cup",
#         "price": "8.00",
#         "stock": 2
#     },
#     {
#         "id": "efe0c7a3-9835-4dfb-87e1-575b7d06701a",
#         "name": "Herb caps",
#         "price": "12.00",
#         "stock": 2
#     },
#     {
#         "id": "x341115a-63d2-42ce-8fe0-5f696ecdfca6",
#         "name": "Audiophile Headphones",
#         "price": "550.00",
#         "stock": 2
#     },
#     {
#         "id": "42860491-9f15-43d4-adeb-0db2cc99174a",
#         "name": "Digital Camera",
#         "price": "225.00",
#         "stock": 2
#     },
#     {
#         "id": "63a3c635-4505-4588-8457-ed04fbb76511",
#         "name": "Empty Bluray Disc",
#         "price": "5.00",
#         "stock": 2
#     },
#     {
#         "id": "97a19842-db31-4537-9241-5053d7c96239",
#         "name": "256GB Pendrive",
#         "price": "60.00",
#         "stock": 2
#     }
# ]
# srialize_product = json.dumps(products_backup)
# r.set('products', srialize_product)

def index(request):
    user_session = getUserSessionId(request)
    uid = getUserId(request)
    products = getProducts(-1)
    orders = getOrdersByUserId(user_session)
    total_orders_sum = getTotalSumAllOrders(user_session)
    return render(request, 'index.html',
                  {'products': products,
                   'user_session': user_session,
                   'user_id': uid,
                   'username': getUserName(uid),
                   'cart': getCartByUserSessionSql(user_session),
                   'orders': orders,
                   'orders_total': total_orders_sum,
                   'totalSum': 0.0,
                   'message': showMessage(request),
                   'page_numbers': getProductPagesTotal(100),
                   })


def page(request, pagenumber):
    userid = getUserSessionId(request)
    msg = request.session['message'] if 'message' in request.session else ""
    request.session['message'] = ""
    products = getProducts(pagenumber)
    orders = getOrdersByUserId(userid)
    total_orders_sum = getTotalSumAllOrders(userid)
    return render(request, 'index.html',
                  {'products': products,
                   'userid': userid,
                   'username': request.session['username'] if 'username' in request.session else "Undefined",
                   'cart': getCartByUserSessionSql(userid),
                   'orders': orders,
                   'orders_total': total_orders_sum,
                   'total_sum': 0.0,
                   'message': msg,
                   'page_numbers': getProductPagesTotal(10),
                   })


def add(request, productid):
    userid = getUserSessionId(request)
    # putToCart(userid, productid)
    putToCartSql(userid, productid)
    return redirect(index)
    # return render(request, 'add.html', {'response': response, 'user': request.session['user']})


def makeorder(request):
    uid = getUserId(request)
    if uid == 0:
        setMessage(request, "You must login before order", "warning")
        return redirect(login)
    user_session = getUserSessionId(request)
    new_order_id = makeOrder(uid, user_session)
    setMessage(request, "Your order number is " + str(new_order_id))
    return redirect(index)


def savename(request, action='save'):
    if 'user' not in request.session:
        request.session['user'] = request.session._get_or_create_session_key()
        request.session['username'] = request.POST.get("username", "Undefined")
    if action == 'edit':
        request.session['username'] = "Undefined"
    elif request.POST.get("username"):
        request.session['username'] = request.POST.get("username")
    return redirect(index)


def showorders(request):
    user_session = getUserSessionId(request)
    uid = getUserId(request)
    orders = getOrdersByUserId(uid)
    total_orders_sum = getTotalSumAllOrders(uid)
    return render(request, 'orders.html',
                  {
                      'user_session': user_session,
                      'user_id': uid,
                      'username': getUserName(uid),
                      'cart': getCartByUserSessionSql(user_session),
                      'orders': orders,
                      'orders_total': total_orders_sum,
                      'totalSum': 0.0,
                  })


def showorder(request, orderid):
    uid = getUserId(request)
    user_session = getUserSessionId(request)
    order = getOrderById(orderid, uid)
    if "id" not in order:
        return render(request, '404.html')
    if "uid" in order and uid != order['user_id']:
        return render(request, '403.html')
    return render(request, 'order.html',
                  {
                      'user_session': user_session,
                      'user_id': uid,
                      'username': getUserName(uid),
                      'cart': getCartByUserSessionSql(user_session),
                      'order': order,
                  })


def login(request):
    user_session = getUserSessionId(request)
    uid = getUserId(request)
    if uid == 0 and request.POST.get("login"):
        uid = checkLoginPassword(request.POST.get("login"), request.POST.get("password"))
        if uid != 0:
            loginUser(request, uid)
            setMessage(request, "Welcome " + getUserName(uid))
        else:
            setMessage(request, "Wrong login/password", "danger")
        return redirect(login)
    return render(request, 'login.html',
                  {
                      'user_session': user_session,
                      'user_id': uid,
                      'username': getUserName(uid),
                      'cart': getCartByUserSessionSql(user_session),
                      'message': showMessage(request),
                  })


def logout(request):
    logoutUser(request)
    return redirect(index)

# r.close()
