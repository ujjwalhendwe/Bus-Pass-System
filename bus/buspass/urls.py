from django.urls import path
from . import views

urlpatterns = [
    path('',views.register),
    path('update',views.update),
    path('login',views.login)
]
