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
    path('history',views.history),
    path('cancel/<Ticketno>',views.cancel),
    path('profile',views.profile),
    path('editprofile',views.editprofile),
    path('edit',views.edit),
    path('trackbus',views.trackbus),
    path('buspass',views.buspass), 
    path('passcheck',views.passcheck)
]

