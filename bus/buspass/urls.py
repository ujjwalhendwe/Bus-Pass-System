from django.urls import path
from . import views

urlpatterns = [
    path('',views.signin),
    path('update',views.update),
    path('register',views.register),
    path('login',views.login),
    path('showbus',views.showbus),
    path('track',views.track),
    path('trackbus',views.trackbus)
]
