import os
from celery import Celery
import multiprocessing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sales_trading_app.settings')

if os.name != "nt":
    multiprocessing.set_start_method("fork", force=True)

celery_app = Celery('sales_trading_app')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()


