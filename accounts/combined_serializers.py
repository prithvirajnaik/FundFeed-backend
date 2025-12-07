from django.contrib.auth import get_user_model
from rest_framework import serializers

# from .models import DeveloperProfile, InvestorProfile
from .profile_serializers import DeveloperProfileSerializer, InvestorProfileSerializer

User = get_user_model()

class FullUserSerializer(serializers.ModelSerializer):
    developer_profile = DeveloperProfileSerializer(read_only=True)
    investor_profile = InvestorProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "role",
            "avatar_url",
            "location",
            "developer_profile",
            "investor_profile",
        ]
