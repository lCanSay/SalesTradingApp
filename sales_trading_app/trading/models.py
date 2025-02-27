from django.db import models

from products.models import Product
from users.models import User

class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES)
    status = models.CharField(max_length=19, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.order_type} order for {self.product.name} by {self.user.username}"
    
class Transaction(models.Model):
    buy_order = models.ForeignKey(Order, related_name='buy_transactions', on_delete=models.CASCADE)
    sell_order = models.ForeignKey(Order, related_name='sell_transactions', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction between {self.buy_order.user.username} and {self.sell_order.user.username}"