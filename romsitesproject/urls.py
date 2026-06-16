"""
URL configuration for romsitesproject project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('romsitesapp.urls')), # Route home and app views
]
