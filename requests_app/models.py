# requests_app/models.py
from django.db import models
from accounts.models import User
from pitches.models import Pitch
from investor_posts.models import InvestorPost
import uuid

def gen_uuid():
    return str(uuid.uuid4())

class ContactRequest(models.Model):
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
