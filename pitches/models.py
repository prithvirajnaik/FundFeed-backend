from cloudinary_storage.storage import MediaCloudinaryStorage

# pitches/models.py
from django.db import models
from accounts.models import User
import uuid

def gen_uuid():
    return str(uuid.uuid4())

class Pitch(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=gen_uuid, editable=False)
    developer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pitches")
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=300)
    tags = models.JSONField(default=list, blank=True)
    funding_stage = models.CharField(max_length=30, blank=True)
    ask = models.CharField(max_length=150, blank=True)
    video = models.FileField(upload_to="pitches/videos/", storage=MediaCloudinaryStorage() )
    thumbnail = models.ImageField(upload_to="pitches/thumbnails/", null=True, blank=True)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class SavedPitch(models.Model):
    investor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_pitches")
    pitch = models.ForeignKey(Pitch, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("investor", "pitch")

