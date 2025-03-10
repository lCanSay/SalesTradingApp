from .models import Order, Transaction
from users.views import IsOwnerOrAdmin
from .serializers import OrderSerializer, TransactionSerializer
from sales_trading_app.utils import send_order_notification

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, permissions, status, generics
from django.shortcuts import get_object_or_404

from io import BytesIO
from django.http import HttpResponse
from django.utils import timezone
from reportlab.pdfgen import canvas

class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_staff
    
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]  

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        elif self.action in ['create']:
            return [permissions.IsAuthenticated()]
        return [permission() for permission in self.permission_classes]

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Transaction.objects.all()
        return Transaction.objects.filter(user=user)
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:  
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    
class BuyOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, order_type='SELL', status='PENDING')

        buy_order = Order.objects.create(
            user=request.user,
            product=order.product,
            quantity=order.quantity,
            price=order.price,
            order_type='BUY',
            status='FULFILLED'
        )

        transaction = Transaction.objects.create(
            buy_order=buy_order,
            sell_order=order,
            quantity=order.quantity,
            price=order.price
        )

        order.status = 'FULFILLED'
        order.save()

        buyer = request.user
        seller = order.user
        subject = "Your order has been bought!"
        message = f"Hello {seller.username},\n\nYour order for {order.quantity} {order.product} at {order.price} has been purchased by {buyer.username}!"
        send_order_notification.delay(seller.email, subject, message)

        return Response(
            {"message": "Order successfully purchased", "transaction": TransactionSerializer(transaction).data},
            status=status.HTTP_201_CREATED
        )

class SellOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, order_type='BUY', status='PENDING')

        sell_order = Order.objects.create(
            user=request.user,
            product=order.product,
            quantity=order.quantity,
            price=order.price,
            order_type='SELL',
            status='FULFILLED'
        )

        transaction = Transaction.objects.create(
            buy_order=order,
            sell_order=sell_order,
            quantity=order.quantity,
            price=order.price
        )

        order.status = 'FULFILLED'
        order.save()

        seller = request.user
        buyer = order.user
        subject = "Your order has been sold!"
        message = f"Hello {buyer.username},\n\nYour order for {order.quantity} {order.product} at {order.price} has been sold to {seller.username}!"
        send_order_notification.delay(buyer.email, subject, message)

        return Response(
            {"message": "Order successfully sold", "transaction": TransactionSerializer(transaction).data},
            status=status.HTTP_201_CREATED
        )

class InvoiceRetrievePDFView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def retrieve(self, request, *args, **kwargs):
        order = self.get_object()
        
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer)
        
        pdf.drawString(100, 800, f"Invoice for Order #{order.id}")
        pdf.drawString(100, 780, f"User: {order.user.username}")
        pdf.drawString(100, 760, f"Product: {order.product.name}")
        pdf.drawString(100, 740, f"Quantity: {order.quantity}")
        pdf.drawString(100, 720, f"Price per Unit: ${order.price}")
        pdf.drawString(100, 700, f"Total Price: ${order.total_price}")
        pdf.drawString(100, 680, f"Status: {order.get_status_display()}")
        pdf.drawString(100, 660, f"Created At: {order.created_at.strftime('%Y-%m-%d')}")
        pdf.drawString(100, 640, f"Date: {timezone.now().strftime('%Y-%m-%d')}")

        pdf.showPage()
        pdf.save()

        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
        return response
