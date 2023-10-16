from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
import requests
import redis
import json
import sys


r = redis.StrictRedis(
    # host='10.21.17.68',
    host='127.0.0.1',
    port=6379,
    password='please',
    charset="utf-8",
    decode_responses=True
)

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
    if 'user' not in request.session:
        request.session['user'] = request.session._get_or_create_session_key()
    userid = request.session['user']
    cartid = 'cart-' + userid
    json_cart = r.get(cartid)
    json_products = r.get('products')
    products = json.loads(json_products)
    if json_cart:
        cart = json.loads(json_cart)
    else:
        cart = []
    totalSum = 0.0
    for product in products:
        for c in cart:
            if c['product_id'] == product['id']:
                c['name'] = product['name']
                c['price'] = product['price']
                totalSum += float(c['price']) * float(c['quantity'])
    return render(request, 'base.html', {'products': products, 'user': userid, 'cart': cart, 'totalSum': totalSum})

def add(request, productid):
    if 'user' not in request.session:
        request.session['user'] = request.session._get_or_create_session_key()
    userid = request.session['user']
    cartid = 'cart-' + userid
    json_cart = r.get(cartid)
    if json_cart:
        cart = json.loads(json_cart)
    else:
        cart = []
    productAlreadyInCart = False
    for product in cart:
        if product['product_id'] == productid:
            product['quantity'] += 1
            productAlreadyInCart = True
            break
    if not productAlreadyInCart:
        cart.append({ "product_id": productid, "quantity": 1 })
    r.set(cartid, json.dumps(cart))
    r.expire(cartid, 600) # Time life of cart in seconds

    response = 'Add to cart ' + str(cart) + ' product is ' + productid

    return redirect(index)
    # return render(request, 'add.html', {'response': response, 'user': request.session['user']})

r.close()
