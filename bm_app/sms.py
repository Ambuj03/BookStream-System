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
    if not receipt.customer or not receipt.customer.customer_phone:
        return False, "No customer phone available"
    
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    phone = receipt.customer.customer_phone.strip()
    if not phone.startswith('+'):
        phone = f"+91{phone}"
        
        #EDIT MESSAGE BODY to include book details etc self
    message_body = (
        f"Thank you for your purchase. {receipt.customer.customer_name}!\n\n"
        f"Receipt #{receipt.receipt_id}\n"
        f"Date: {receipt.date.strftime('%d-%m-%Y')}\n"
        f"Amount: ₹{receipt.total_amount}\n"
        f"Distributor: {receipt.distributor.distributor_name}\n\n"
        f"Thank you for supporting {receipt.temple.name}."
    )
    
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