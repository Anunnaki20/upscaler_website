
from django.urls import path
from django.contrib import admin
from . import views


urlpatterns = [
    path('test/', views.test_connection, name='test'),
]