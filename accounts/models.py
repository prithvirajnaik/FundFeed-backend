from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

def gen_uuid():
    return str(uuid.uuid4())


class User(AbstractUser):
    STATUS_CHOICES = (
        ("pending", "Pending Verification"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )
    id = models.CharField(max_length=50, primary_key=True, default=gen_uuid, editable=False)

    # override AbstractUser's username so it is NOT unique
    username = models.CharField(
        max_length=150,
        unique=False,
        blank=True,
        null=True,
    )

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20, 
        choices=(("developer", "developer"), ("investor", "investor")),
        default="developer"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending"
    )

    avatar_url = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=120, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # if you still want to collect username

    def __str__(self):
        return self.email


class DeveloperProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="developer_profile")
    title = models.CharField(max_length=120, blank=True)
    bio = models.CharField(max_length=300, blank=True)
    skills = models.JSONField(default=list, blank=True)
    github = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    portfolio = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} DeveloperProfile"


class InvestorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="investor_profile")
    firm = models.CharField(max_length=150, blank=True)
    investor_type = models.CharField(max_length=50, blank=True)
    contact_preference = models.CharField(max_length=20, default="email")
    stages = models.JSONField(default=list, blank=True)
    sectors = models.JSONField(default=list, blank=True)
    linkedin = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} InvestorProfile"
