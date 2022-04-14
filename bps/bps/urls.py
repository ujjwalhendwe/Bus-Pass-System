from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', TemplateView.as_view(template_name='dashboard/home.html'), name='home'),
    path('accounts/', include('allauth.urls')),
    #path('hemlo/', TemplateView.as_view(template_name='account/temp.html')),
    path('tracking/', TemplateView.as_view(template_name='Trackbus.html')),
    path('',include('bus.urls')),
    
]
