from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_booking_confirmation_email(email, booking_details):
    subject = 'Booking Confirmation'
    message = f"Thank you for booking with ALX Travel! \n\nBooking Details:\n{booking_details}"
    sender = settings.DEFAULT_FROM_EMAIL
    recipients = [email]

    send_mail(subject, message, sender, recipients)
    return f"Confirmation email sent to {email}"
