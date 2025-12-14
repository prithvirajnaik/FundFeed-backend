# requests_app/models.py
from django.db import models
from accounts.models import User
from pitches.models import Pitch
from investor_posts.models import InvestorPost
import uuid

def gen_uuid():
    return str(uuid.uuid4())

class ContactRequest(models.Model):
    MEETING_STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    MEETING_PLATFORM_CHOICES = [
        ('google-meet', 'Google Meet'),
        ('zoom', 'Zoom'),
        ('microsoft-teams', 'Microsoft Teams'),
        ('phone', 'Phone Call'),
        ('in-person', 'In-Person'),
        ('other', 'Other'),
    ]
    
    id = models.CharField(max_length=50, primary_key=True, default=gen_uuid, editable=False)
    developer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_requests")
    investor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    pitch = models.ForeignKey(Pitch, null=True, blank=True, on_delete=models.SET_NULL)
    investor_post = models.ForeignKey(InvestorPost, null=True, blank=True, on_delete=models.SET_NULL)
    message = models.TextField()
    meeting_link = models.TextField(blank=True, null=True)
    preference = models.CharField(max_length=10, choices=(("email","email"),("phone","phone"),("dm","dm")), default="email")
    viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Meeting scheduling fields
    scheduled_start_time = models.DateTimeField(null=True, blank=True, help_text="Scheduled start time for the meeting")
    scheduled_end_time = models.DateTimeField(null=True, blank=True, help_text="Scheduled end time for the meeting")
    meeting_status = models.CharField(max_length=20, choices=MEETING_STATUS_CHOICES, default='scheduled', null=True, blank=True)
    meeting_summary = models.TextField(blank=True, null=True, help_text="Generated summary of the meeting")
    meeting_started_at = models.DateTimeField(null=True, blank=True, help_text="Actual time when meeting started")
    meeting_ended_at = models.DateTimeField(null=True, blank=True, help_text="Actual time when meeting ended")
    
    # New enhanced fields
    timezone = models.CharField(max_length=50, default='UTC', help_text="Timezone for the meeting (e.g., America/New_York)")
    meeting_platform = models.CharField(max_length=20, choices=MEETING_PLATFORM_CHOICES, default='google-meet', null=True, blank=True)
    agenda = models.TextField(blank=True, null=True, help_text="Meeting agenda or discussion topics")


class MeetingSummary(models.Model):
    """Structured meeting summary with discussion points, action items, decisions, and next steps"""
    id = models.CharField(max_length=50, primary_key=True, default=gen_uuid, editable=False)
    contact_request = models.OneToOneField(ContactRequest, on_delete=models.CASCADE, related_name='structured_summary')
    
    # Structured summary data stored as JSON
    discussion_points = models.JSONField(default=list, help_text="List of key discussion points")
    action_items = models.JSONField(default=list, help_text="List of action items with assignee and due date")
    decisions_made = models.JSONField(default=list, help_text="List of decisions made during meeting")
    next_steps = models.TextField(blank=True, null=True, help_text="Overall next steps and follow-up plan")
    
    # Follow-up meeting
    needs_followup = models.BooleanField(default=False)
    followup_date = models.DateTimeField(null=True, blank=True, help_text="Proposed follow-up meeting date")
    
    # Additional notes
    additional_notes = models.TextField(blank=True, null=True, help_text="Any additional notes or observations")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Summary for meeting {self.contact_request.id}"
