from rest_framework import viewsets, permissions, generics
from rest_framework.permissions import BasePermission
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff
    
class UserViewSet(viewsets.ModelViewSet):
    User = get_user_model() 
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsOwnerOrAdmin()]
        return super().get_permissions()