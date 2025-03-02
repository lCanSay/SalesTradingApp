from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserDetailView, UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', UserDetailView.as_view(), name='user-profile'),
]