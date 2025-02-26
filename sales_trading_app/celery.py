import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_trading_app.settings')
app = Celery('sales_trading_app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()