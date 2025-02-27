from django.http import JsonResponse
from rest_framework import viewsets, permissions

from products.forms import ProductEditForm, ProductForm
from users.authentication import CookieJWTAuthentication
from .models import Product
from .serializers import ProductSerializer
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.views.decorators.csrf import csrf_exempt

    
# class IsAdminOrTrader(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return request.user.role in ['ADMIN', 'TRADER']

# class ProductViewSet(viewsets.ModelViewSet):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     permission_classes = [permissions.IsAuthenticated, IsAdminOrTrader]

#     def get_permissions(self):
#         if self.action in ['list', 'retrieve']:
#             return [permissions.AllowAny()]
#         return [permission() for permission in self.permission_classes]
    
# --------------------------

@csrf_exempt
def product_list(request):
    try:
        print("Attempting to authenticate user using JWT")  # Debug print
        jwt_auth = CookieJWTAuthentication()
        auth_result = jwt_auth.authenticate(request)
        if auth_result is None:
            print("Authentication failed: No credentials provided")  # Debug print
            return JsonResponse({'error': 'Authentication credentials were not provided.'}, status=401)
        
        user, _ = auth_result
        if user:
            print(f"User authenticated: {user.username}")  # Debug print
            products = Product.objects.all()
            return render(request, 'products/product_list.html', {'products': products})
        else:
            print("Authentication failed: Invalid user")  # Debug print
            return JsonResponse({'error': 'Unauthorized'}, status=401)
    except AuthenticationFailed as e:
        print(f"Authentication failed: {str(e)}")  # Debug print
        return JsonResponse({'error': str(e)}, status=401)

@csrf_exempt
def product_create(request):
    try:
        jwt_auth = CookieJWTAuthentication()
        user, _ = jwt_auth.authenticate(request)
        if user and user.role in ['ADMIN', 'TRADER']:
            if request.method == 'POST':
                form = ProductForm(request.POST, request.FILES)
                if form.is_valid():
                    form.save()
                    return redirect('product-list')
            else:
                form = ProductForm()
            return render(request, 'products/product_form.html', {'form': form})
        else:
            return JsonResponse({'error': 'You dont have rights to create.'}, status=401)
    except AuthenticationFailed:
        return JsonResponse({'error': 'Invalid token'}, status=401)
    
    
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