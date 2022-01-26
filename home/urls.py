
from django.urls import path
from django.contrib import admin
from . import views


urlpatterns = [
    path('', views.loginPage, name='login'),        # Login is the default page
     path('signup/', views.signupPage, name='signup'),
]