from django import forms
from .models import Order
from products.models import Product

class BuySellOrderForm(forms.ModelForm):
    ORDER_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]

    order_type = forms.ChoiceField(choices=ORDER_TYPES, widget=forms.RadioSelect)

    class Meta:
        model = Order
        fields = ['product', 'quantity', 'price', 'order_type']
