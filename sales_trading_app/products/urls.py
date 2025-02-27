from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import edit_product, product_create, product_list

# from .views import ProductViewSet
# router = DefaultRouter()
# router.register(r'products', ProductViewSet)

urlpatterns = [
    # path('', include(router.urls)),
    path('', product_list, name='product-list'),
    path('create/', product_create, name='product-create'),
    path('edit/<int:product_id>/', edit_product, name='edit-product'),
]