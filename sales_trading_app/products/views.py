from rest_framework import viewsets, permissions

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class IsAdminOrTrader(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['ADMIN', 'TRADER']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    permission_classes = [permissions.IsAuthenticated, IsAdminOrTrader]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminOrTrader()]
    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrTrader]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [IsAdminOrTrader()]