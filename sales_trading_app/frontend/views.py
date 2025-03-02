from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import LoginForm, ProfileForm, RegistrationForm
from .forms import ProductForm
from products.models import Product
from trading.models import Order, Transaction
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse

from trading.serializers import OrderSerializer
from .forms import BuySellOrderForm
from rest_framework import generics
from reportlab.pdfgen import canvas
from io import BytesIO
from rest_framework.permissions import AllowAny

from reportlab.lib.pagesizes import A4
from django.db import models




@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                messages.success(request, f"Welcome, {user.username}!")
                return redirect('frontend:product-list')
    else:
        form = LoginForm()
    return render(request, 'frontend/login.html', {'form': form})

@csrf_exempt
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful. Please log in.")
            return redirect('users/login')
    else:
        form = RegistrationForm()
    return render(request, 'frontend/register.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('frontend:login')


@csrf_exempt
def profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('frontend:profile')
    else:
        form = ProfileForm(instance=user)
    return render(request, 'frontend/profile.html', {'form': form})


# ---------------------------Products-----------------------------------------

@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'frontend/product_list.html', {'products': products})


@login_required
def product_create(request):
    if request.user.role in ['ADMIN', 'TRADER']:
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('frontend:product-list')
        else:
            form = ProductForm()
        return render(request, 'frontend/product_form.html', {'form': form})
    else:
        return JsonResponse({'error': 'You do not have permission to create products.'}, status=403)
    
    
@csrf_exempt
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.role != 'ADMIN':
        return redirect('frontend:product-list')

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('frontend:product-list')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'frontend/edit_product.html', {'form': form, 'product': product})

# ---------------------------Trading-----------------------------------------


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
            return redirect('frontend:order-list')
    else:
        form = BuySellOrderForm()
    return render(request, 'trading/place_order.html', {'form': form})

@login_required
def buy_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, order_type='SELL', status='PENDING')
    if request.method == 'POST':

        Transaction.objects.create(
            buy_order=Order.objects.create(
                user=request.user,
                product=order.product,
                quantity=order.quantity,
                price=order.price,
                order_type='BUY',
                status='FULFILLED'
            ),
            sell_order=order,
            quantity=order.quantity,
            price=order.price
        )
        
        order.status = 'FULFILLED'
        order.save()
        messages.success(request, "You have successfully purchased the product.")

        return redirect('frontend:order-list')
    return render(request, 'trading/buy_order.html', {'order': order})

@login_required
def sell_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, order_type='BUY', status='PENDING')

    if request.method == 'POST':
        Transaction.objects.create(
            buy_order=order,
            sell_order=Order.objects.create(
                user=request.user,
                product=order.product,
                quantity=order.quantity,
                price=order.price,
                order_type='SELL',
                status='FULFILLED'
            ),
            quantity=order.quantity,
            price=order.price
        )

        order.status = 'FULFILLED'
        order.save()
        messages.success(request, "You have successfully sold the product.")

        return redirect('frontend:order-list')
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
    

@login_required
def user_transactions(request):
    transactions = Transaction.objects.filter(
        models.Q(buy_order__user=request.user) | models.Q(sell_order__user=request.user)
    ).order_by('-created_at')

    return render(request, 'frontend/user_transactions.html', {'transactions': transactions})
