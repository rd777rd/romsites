from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about', views.about_view, name='about'),
    path('portfolio', views.portfolio_view, name='portfolio'),
    path('services', views.services_view, name='services'),
    path('design', views.design_view, name='design'),
    path('development', views.development_view, name='development'),
    path('maintenance', views.maintenance_view, name='maintenance'),
    path('seo', views.seo_view, name='seo'),
    path('delete-review/<int:review_id>', views.delete_review_view, name='delete_review'),
]
