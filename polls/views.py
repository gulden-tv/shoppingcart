from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    if 'cart' not in request.session:
        request.session['cart'] = request.session._get_or_create_session_key()
    return HttpResponse("Hello, world. " + str(request.session['cart']))

def add(request):
    if 'cart' not in request.session:
        request.session['cart'] = request.session._get_or_create_session_key()
    return HttpResponse("Add to cart. " + str(request.session['cart']))
