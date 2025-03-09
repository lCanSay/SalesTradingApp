from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_order_notification(user_email, subject, message):
    logger.info(f"📩 Attempting to send email to: {user_email}")


    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user_email],
            fail_silently=False,
        )
        logger.info("✅ Email sent successfully!")

    except Exception as e:
        logger.error(f"❌ Email sending failed: {e}")

