from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("page/<pagenumber>", views.page, name="index"),
    path('add/<productid>', views.add, name="add"),
    path('make-order/', views.makeorder, name="makeorder"),
    path('orders/', views.showorders, name="showorders"),
    path('order/<orderid>', views.showorder, name="showorder"),
    path('save-name/<action>', views.savename, name="savename")
]


