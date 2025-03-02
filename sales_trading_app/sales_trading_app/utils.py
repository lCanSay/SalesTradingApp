from django.core.mail import send_mail
from django.conf import settings

def send_order_notification(user_email, subject, message):
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
    )
