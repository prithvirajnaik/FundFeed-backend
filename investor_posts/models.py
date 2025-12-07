# investor_posts/models.py
from django.db import models
from accounts.models import User
import uuid

def gen_uuid():
    return str(uuid.uuid4())

class InvestorPost(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=gen_uuid, editable=False)
    investor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="investor_posts")
    title = models.CharField(max_length=150)
    description = models.TextField()
    tags = models.JSONField(default=list, blank=True)
    stages = models.JSONField(default=list, blank=True)
    amount_range = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=120, blank=True)
    contact_preference = models.CharField(max_length=20, default="email")
    logo = models.ImageField(upload_to="investor/logos/", null=True, blank=True)
    views = models.IntegerField(default=0)
    saved_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class SavedInvestorPost(models.Model):
    developer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_investor_posts")
    post = models.ForeignKey(InvestorPost, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("developer", "post")
