from django.contrib import admin

from trading.models import Order, Transaction


admin.site.register(Order)
admin.site.register(Transaction)