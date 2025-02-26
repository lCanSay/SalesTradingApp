from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import refresh_token, user_login, register

urlpatterns = [
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('refresh-token/', refresh_token, name='refresh-token'),
]