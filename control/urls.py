#-_- coding: utf-8 -_-
from django.conf.urls          import url, include
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    url('login$', views.Login, name='Login'),
]
