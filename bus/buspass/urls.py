from django.urls import path
from django.conf import settings
from django.conf.urls.static import static 
from . import views

urlpatterns = [
    path('',views.signin),
    path('update',views.update),
    path('register',views.register),
    path('login',views.login),
    path('showbus',views.showbus),
    path('track',views.track),
    path('buspass',views.buspass),
    path('passcheck',views.passcheck),
    path('trackbus',views.trackbus)
]

