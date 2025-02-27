from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import refresh_token, user_login, register, user_logout, profile

urlpatterns = [
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('refresh-token/', refresh_token, name='refresh-token'),
    path('profile/', profile, name='profile'),
    path('logout/', user_logout, name='logout'),
]