from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from trading.serializers import OrderSerializer
from trading.forms import BuySellOrderForm
from rest_framework import generics
from reportlab.pdfgen import canvas
from io import BytesIO
from rest_framework.permissions import AllowAny

from .models import Order

def buy_sell(request):
    return render(request, 'trading/buy_sell.html')

def orders(request):
    return render(request, 'trading/orders.html')

@login_required
def place_order(request):
    if request.method == 'POST':
        form = BuySellOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            return redirect('order-list')
    else:
        form = BuySellOrderForm()
    return render(request, 'trading/place_order.html', {'form': form})

@login_required
def buy_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, order_type='SELL', status='PENDING')
    if request.method == 'POST':
        order.status = 'FULFILLED'
        order.save()
        return redirect('order-list')
    return render(request, 'trading/buy_order.html', {'order': order})

@login_required
def sell_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, order_type='BUY', status='PENDING')
    if request.method == 'POST':
        order.status = 'FULFILLED'
        order.save()
        return redirect('order-list')
    return render(request, 'trading/sell_order.html', {'order': order})

def order_list(request):
    sell_orders = Order.objects.filter(order_type='SELL', status='PENDING').exclude(user=request.user)
    buy_orders = Order.objects.filter(order_type='BUY', status='PENDING').exclude(user=request.user)

    return render(request, 'trading/order_list.html', {
        'sell_orders': sell_orders,
        'buy_orders': buy_orders,
    })

@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'trading/user_orders.html', {'orders': orders})

class InvoiceRetrievePDFView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

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
        pdf.drawString(100, 660, f"Created At: {order.created_at}")
        pdf.drawString(100, 640, f"Date: {timezone.now().strftime('%Y-%m-%d')}")

        pdf.showPage()
        pdf.save()

        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
        return response