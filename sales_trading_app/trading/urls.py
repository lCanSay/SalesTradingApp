from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BuyOrderView, InvoiceRetrievePDFView,SellOrderView, OrderViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'transactions', TransactionViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('buy/{order_id}/', BuyOrderView.as_view(), name='buy-order'),
    path('sell/{order_id}/', SellOrderView.as_view(), name='sell-order'),
    path('{order_id}/invoice/', InvoiceRetrievePDFView.as_view(), name='order-invoice'),

]