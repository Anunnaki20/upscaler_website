from django.conf import settings # new
from django.conf.urls.static import static # new
from django.urls import path
from django.contrib import admin
from . import views


urlpatterns = [
    path('', views.loginPage, name='login'),        # Login is the default page
     path('signup/', views.signupPage, name='signup'),
     path('clean/', views.cleanDirectories, name='cleanDirectories'),
     path("upload/", views.upload, name="upload"),
     path("download/", views.download_file, name="download_file"),
     path("download//", views.download_file, name="download_file"),
     path("test/", views.test_connection),
    #  path("download/", views.download, name="download"),
]

if settings.DEBUG: # new
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)