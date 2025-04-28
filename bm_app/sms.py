from twilio.rest import Client
from django.utils import timezone
import logging, os

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')   
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

def send_receipt_sms(receipt):

    from .models import ReceiptBooks

    if not receipt.customer or not receipt.customer.customer_phone:
        return False, "No customer phone available"
    
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    phone = receipt.customer.customer_phone.strip()
    if not phone.startswith('+'):
        phone = f"+91{phone}"
        
    
    receipt_books = ReceiptBooks.objects.filter(receipt_id = receipt.receipt_id)

    #EDIT MESSAGE BODY to include book details etc self
    book_details = ""
    for idx, rb in enumerate(receipt_books, 1):
        book_details += f"{idx}. {rb.book_name} x {rb.quantity} - ₹{rb.quantity * rb.book_price}\n"
    

    #for trial limited length twilio account

    message_body = (
        f"Dear {receipt.customer.customer_name},\n\n"
        f"Thank you for your purchase from {receipt.temple.name}!\n\n"
        f"RECEIPT #{receipt.receipt_id}\n"
        f"Date: {receipt.date.strftime('%d-%m-%Y')}\n\n"
        f"Total: ₹{receipt.total_amount}\n\n"
        f"Hare Krishna! 🙏"
    )

    #Use this with pro twilio acc
    # message_body = (
    #     f"Dear {receipt.customer.customer_name},\n\n"
    #     f"Thank you for your purchase from {receipt.temple.name}!\n\n"
    #     f"RECEIPT #{receipt.receipt_id}\n"
    #     f"Date: {receipt.date.strftime('%d-%m-%Y')}\n\n"
    #     f"ITEMS:\n{book_details}\n"
    #     f"Total: ₹{receipt.total_amount}\n\n"
    #     f"Our best wishes for your spiritual journey. For any queries please contact your distributor: {receipt.distributor.distributor_name}.\n\n"
    #     f"Hare Krishna! 🙏"
    # )

    print(message_body)
    
    try:
        message = client.messages.create(
            body = message_body,
            from_ =TWILIO_PHONE_NUMBER,
            to = phone
        )
        
        logger.info(f"SMS sent to {phone} for receipt #{receipt.receipt_id}, SID: {message.sid}")
        
        receipt.notification_sent = True
        receipt.notification_status = 'SENT'
        receipt.notification_timestamp = timezone.now()
        receipt.save(update_fields=['notification_sent', 'notification_status', 'notification_timestamp'])

        return True, message.sid
    
    except Exception as e:
        error_msg = f"Failed to send SMS for receipt #{receipt.receipt_id}: {str(e)}"
        logger.error(error_msg)
        return False, error_msg