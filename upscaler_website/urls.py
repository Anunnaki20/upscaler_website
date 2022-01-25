# Handles all the core URL routing

from xml.etree.ElementInclude import include
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('admin/', admin.site.urls, name='admin'),
    path('', include('home.urls'))
]

