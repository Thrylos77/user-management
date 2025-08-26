from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging
import random

def generate_otp():
    return f"{random.randint(100000, 999999)}"

logger = logging.getLogger(__name__)
def send_otp_email(email: str, otp: str):
    """
    Sends the OTP to the user's email address using an HTML template.
    """
    subject = 'Your One-Time Password (OTP) for Password Reset'
    context = {'otp': otp}
    html_message = render_to_string('emails/otp_email.html', context)
    plain_message = strip_tags(html_message)
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    
    try:
        send_mail(subject, plain_message, email_from, recipient_list, html_message=html_message, fail_silently=False)
        logger.info(f"Successfully sent OTP to {email}")
    except Exception as e:
        logger.error(f"Error sending OTP to {email}: {e}")
