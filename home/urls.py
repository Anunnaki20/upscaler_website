from django.conf import settings # new
from django.conf.urls.static import static # new
from django.urls import path
from django.contrib import admin
from . import views


urlpatterns = [
    path('login/', views.loginPage, name='login'),        
    path('signup/', views.signupPage, name='signup'),
    path('logout/', views.logoutUser, name='logout'),
    path('', views.upload, name="upload"), # Upload is the default page
    path('downloadZip/', views.downloadZip, name="downloadZip"),
    path('sendBackZip/', views.sendBackZip, name="sendBackZip"),
]

if settings.DEBUG: # new
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)