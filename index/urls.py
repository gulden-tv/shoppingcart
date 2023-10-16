from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('add/<productid>', views.add, name="add"),
    path('make-order/', views.makeorder, name="makeorder"),
    path('save-name/<action>', views.savename, name="savename")
]


