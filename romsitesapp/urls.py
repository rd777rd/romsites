from django.urls import path
from . import views
from .views import About, Portfolio, ReviewDeleteView

urlpatterns = [
    path('', views.home, name="home"),
    path('about/', About.as_view(), name="about"),
    path('portfolio/', Portfolio.as_view(), name="portfolio"),
    path('services/', views.services, name='services'),
    path('design/', views.design, name='design'),
    path('development/', views.development, name='development'),
    path('seo/', views.seo, name='seo'),
    path('maintenance/', views.maintenance, name='maintenance'),
    path('reviews/delete/<int:pk>/', ReviewDeleteView.as_view(), name='delete_review'),
    
]