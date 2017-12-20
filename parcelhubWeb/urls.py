from django.conf.urls import url, include
from . import views
from django.contrib.auth.views import logout
from django.contrib import admin
urlpatterns = [
    url(r'^$', views.loginuser, name='login'),          
    url(r'^logout/$', logout, {'next_page': '/parcelhubWeb/'}, name='logout'),
    

]

