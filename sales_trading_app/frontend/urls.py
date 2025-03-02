from django.urls import path, include
from .views import InvoiceRetrievePDFView, buy_order, buy_sell, edit_product, order_list, place_order, product_create, product_list, sell_order, user_login, register, user_logout, profile, user_orders

app_name = "frontend"

urlpatterns = [
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('logout/', user_logout, name='logout'),

    path('product-list/', product_list, name='product-list'),
    path('create/', product_create, name='product-create'),
    path('edit/<int:product_id>/', edit_product, name='edit-product'),

    path('buy-sell/', buy_sell, name='buy-sell'),
    path('user-orders/', user_orders, name='user-orders'),
    path('place-order/', place_order, name='place-order'),
    path('order-list/', order_list, name='order-list'),
    path('buy/<int:order_id>/', buy_order, name='buy-order'),
    path('sell/<int:order_id>/', sell_order, name='sell-order'),
    path('orders/<int:pk>/invoice/', InvoiceRetrievePDFView.as_view(), name='order-invoice'),
]