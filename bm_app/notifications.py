from django.utils import timezone
from .models import Notification, MasterInventory, DistributorBooks, Temple

LOW_STOCK_THRESHOLD = 10

def create_notification(temple, user_type, user_id, message, event_type):
    
    notification = Notification.objects.create(
        temple = temple,
        user_type = user_type,
        user_id = user_id,
        message = message,
        event_type = event_type,
        created_at = timezone.now(),
        status = 'Unread'
    )
    
    return notification

def check_master_inventory_stock(inventory_item):
    if inventory_item.stock < LOW_STOCK_THRESHOLD:
        admin_id = inventory_item.temple.admin_id
        
        message = f"Low stock alert: '{inventory_item.book.book_name}' has only {inventory_item.stock} copied left in master inventory."
        
        return create_notification(
            temple = inventory_item.temple,
            user_type = 'admin',
            user_id = admin_id,
            message = message,
            event_type='LOW_STOCK'
        )
    return None

def check_distributor_stock(distributor_book):
    if distributor_book.book_stock < LOW_STOCK_THRESHOLD:
        message = f"Low stock alert: '{distributor_book.book_name}' has only {distributor_book.book_stock} copies left in your inventory."
        
        # Create notification for distributor
        return create_notification(
            temple=distributor_book.temple,
            user_type='distributor',
            user_id=distributor_book.distributor.distributor_id,
            message=message,
            event_type='LOW_STOCK'
        )
    return None

def notify_new_book_allocation(distributor, book_name, quantity, temple):
    
    message = f"New lot of book have been allocated: {book_name} : {quantity}"
    
    return create_notification(
        temple = temple,
        user_type = 'distributor',
        user_id = distributor.distributor_id,
        message=message,
        event_type = 'NEW_LOT'
    )
    
def mark_notification_as_read(notification_id):
    
    try: 
        noti = Notification.objects.get(notification_id = notification_id)
        noti.status = 'Read'
        noti.save()
        return True
    except Notification.DoesNotExist:
        return False
    
    
# Functions to load notification for admin and the distributor

def get_admin_notifications(admin_user):
    admin_id = admin_user.id
    admin_notification = Notification.objects.filter(
        user_type='admin',
        user_id=admin_id
    ).order_by('-created_at')
    
    return admin_notification

def get_distributor_notifications(distributor_id):
    
    distributor_notifications = Notification.objects.filter(
        user_type = 'distributor',
        user_id = distributor_id
    )
    return distributor_notifications


def cleanup_old_notifications(days = 45):
    
    cutoff_date = timezone.now() -  timezone.timedelta(days = days)
    old_notifications = Notification.objects.filter(created_at__lt = cutoff_date)
    count = old_notifications.count()
    old_notifications.delete()
    return count


    
    