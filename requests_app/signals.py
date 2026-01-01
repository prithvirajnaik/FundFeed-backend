from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import ContactRequest
import datetime

@receiver(post_save, sender=ContactRequest)
def send_notification_email(sender, instance, created, **kwargs):
    """
    Sends an email notification when a new ContactRequest is created.
    Implements throttling to prevent spam from the same developer to the same investor.
    """
    if not created:
        return

    # Throttling Logic: Check for previous requests in the last 30 minutes
    time_threshold = timezone.now() - datetime.timedelta(minutes=30)
    
    # Check if this sender (developer) sent any OTHER request to this receiver (investor) recently
    recent_requests_count = ContactRequest.objects.filter(
        developer=instance.developer,
        investor=instance.investor,
        created_at__gte=time_threshold
    ).exclude(id=instance.id).count()

    if recent_requests_count > 0:
        print(f"Email Notification Throttled: {instance.developer.email} -> {instance.investor.email} (Recent request exists)")
        return

    # Prepare Email
    recipient = instance.investor
    sender_name = instance.developer.username or instance.developer.email
    subject = f"New Contact Request from {sender_name} on FundFeed"
    
    message_body = (
        f"Hello,\n\n"
        f"You have received a new contact request from {sender_name}.\n\n"
        f"Message:\n{instance.message}\n\n"
        f"Log in to FundFeed to view more details and respond.\n\n"
        f"Best regards,\nThe FundFeed Team"
    )

    try:
        send_mail(
            subject=subject,
            message=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient.email],
            fail_silently=False,
        )
        print(f"Notification Email sent to {recipient.email}")
    except Exception as e:
        print(f"Error sending email: {str(e)}")
