from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import user_login, register, user_logout, profile, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('logout/', user_logout, name='logout'),
]