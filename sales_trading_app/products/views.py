from django.http import JsonResponse
from rest_framework import viewsets, permissions

from products.forms import ProductEditForm, ProductForm
from .models import Product
from .serializers import ProductSerializer
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.exceptions import AuthenticationFailed
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


    
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
        return [permission() for permission in self.permission_classes]
    
# --------------------------

@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})


@login_required
def product_create(request):
    if request.user.role in ['ADMIN', 'TRADER']:
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('product-list')
        else:
            form = ProductForm()
        return render(request, 'products/product_form.html', {'form': form})
    else:
        return JsonResponse({'error': 'You do not have permission to create products.'}, status=403)
    
    
@csrf_exempt
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.role != 'ADMIN':
        return redirect('product-list')

    if request.method == 'POST':
        form = ProductEditForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product-list')
    else:
        form = ProductEditForm(instance=product)
    
    return render(request, 'products/edit_product.html', {'form': form, 'product': product})