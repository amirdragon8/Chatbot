from django.contrib import admin
from django.urls import include, path


from . import views
app_name = 'chat'
urlpatterns = [
    path('chat/', views.chat_view, name='chat'),
    path('form-creation/', views.form_view, name='form'),
    path('user-creation/', views.register_view, name='user'),
    path('vonboard/', views.volunteer_onboard_view, name='volunteer_onboard'),
    path('tasks/<str:username>/', views.user_tasks_view, name='user_tasks'),
    path('show-user/', views.create_and_show_user, name='show_user'),
    path('show-task/', views.create_and_show_task, name='show_task'),
    path('show-schema/', views.show_schema, name='show_schema'),
    path('test1/', views.test_user_registration, name='test_user_registration'),
    path('test2/', views.test_task_creation, name='test_task_creation'),
]