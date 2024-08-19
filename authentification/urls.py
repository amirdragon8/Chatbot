from django.contrib import admin
from django.urls import include, path

from . import views
app_name = 'authentification'
urlpatterns = [
    path('', views.index, name='index' ),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
]