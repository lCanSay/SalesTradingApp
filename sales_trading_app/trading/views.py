from rest_framework import viewsets, permissions
from .models import Order, Transaction
from .serializers import OrderSerializer
from users.views import IsOwnerOrAdmin

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]  

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permission() for permission in self.permission_classes]

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]