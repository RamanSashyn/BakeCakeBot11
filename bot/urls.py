from django.urls import path
from . import views

urlpatterns = [
    path('go/<str:short_url>/', views.redirect_to_original_url, name='redirect_to_original_url'),
]