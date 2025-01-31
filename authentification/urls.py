from django.contrib import admin
from django.urls import include, path

from . import views
app_name = 'authentification'
urlpatterns = [
    path('', views.index, name='index' ),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('complete-npo-profile/', views.complete_npo_profile, name='complete_npo_profile'),
    path('complete-volunteer-profile/', views.complete_volunteer_profile, name='complete_volunteer_profile'),
]