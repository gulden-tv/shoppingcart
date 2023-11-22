from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
import requests
import redis
import json
import sys
import os
from .application import *


def index(request):
    user_session = getUserSessionId(request)
    uid = getUserId(request)
    products = getProducts(-1) # array of products
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
    putToCartSql(userid, productid)
    return redirect(index)


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
    last_login = getLastLoginDate(uid)
    user_login = getUserLogin(uid)
    if uid == 0 and request.POST.get("login"):
        uid = checkLoginPassword(request.POST.get("login"), request.POST.get("password"))
        if uid != 0:
            loginUser(request, uid)
            last_login = getLastLoginDate(uid)
            setMessage(request, "Welcome " + getUserName(uid))
        else:
            setMessage(request, "Wrong login/password", "danger")
        return redirect(login)
    return render(request, 'login.html',
                  {
                      'user_session': user_session,
                      'user_id': uid,
                      'username': getUserName(uid),
                      'user_login': user_login,
                      'last_login': last_login,
                      'cart': getCartByUserSessionSql(user_session),
                      'message': showMessage(request),
                  })


def logout(request):
    logoutUser(request)
    return redirect(index)

# r.close()
