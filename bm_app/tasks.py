from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Notification  # Assuming your model is named Notification

@shared_task
def cleanup_old_notifications():
    """Delete notifications older than 30 days"""
    cutoff_date = timezone.now() - timedelta(days=30)

    print(f"{cutoff_date}")

    old_notifications = Notification.objects.filter(
        created_at__lt=cutoff_date,
        status='Read'  # Only delete read notifications
    )
    deleted_count = old_notifications.count()
    old_notifications.delete()
    return f"Deleted {deleted_count} old notifications"