from django.core.mail import send_mail
from django.conf import settings
import logging
import random

def generate_otp():
    return f"{random.randint(100000, 999999)}"

logger = logging.getLogger(__name__)
def send_otp_email(email: str, otp: str):
    """
    Sends the OTP to the user's email address.
    """
    subject = 'Your One-Time Password (OTP) for Password Reset'
    message = (
        f"Hello,\n\n"
        f"You have requested to reset your password. Use the following One-Time Password (OTP) to proceed:\n\n"
        f"    {otp}\n\n"
        f"This code will expire in 5 minutes. If you did not request a password reset, "
        f"please ignore this email or contact our support team immediately.\n\n"
        f"Thank you,\n"
        f"The Support Team"
    )
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    
    try:
        send_mail(subject, message, email_from, recipient_list, fail_silently=False)
        logger.info(f"Successfully sent OTP to {email}")
    except Exception as e:
        logger.error(f"Error sending OTP to {email}: {e}")
