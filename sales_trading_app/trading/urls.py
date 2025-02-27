from django.urls import path
from .views import InvoiceRetrievePDFView, buy_order, buy_sell, order_list, orders, place_order, sell_order, user_orders

urlpatterns = [
    path('buy-sell/', buy_sell, name='buy-sell'),
    path('user-orders/', user_orders, name='user-orders'),
    path('place-order/', place_order, name='place-order'),
    path('order-list/', order_list, name='order-list'),
    path('buy/<int:order_id>/', buy_order, name='buy-order'),
    path('sell/<int:order_id>/', sell_order, name='sell-order'),
    path('orders/<int:pk>/invoice/', InvoiceRetrievePDFView.as_view(), name='order-invoice'),

]