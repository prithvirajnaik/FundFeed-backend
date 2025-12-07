from rest_framework import serializers
from .models import ContactRequest
from accounts.serializers import UserSerializer
from pitches.serializers import PitchSerializer
from investor_posts.serializers import InvestorPostSerializer


class ContactRequestSerializer(serializers.ModelSerializer):
    developer = UserSerializer(read_only=True)
    investor = UserSerializer(read_only=True)

    pitch = PitchSerializer(read_only=True)
    investor_post = InvestorPostSerializer(read_only=True)

    class Meta:
        model = ContactRequest
        fields = [
            "id",
            "developer",
            "investor",
            "pitch",
            "investor_post",
            "message",
            "meeting_link",
            "preference",
            "viewed",
            "created_at",
        ]


# -----------------------------------------------------
# For creating requests (developer → investor or vice-versa)
# -----------------------------------------------------
class ContactRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactRequest
        fields = [
            "developer",
            "investor",
            "pitch",
            "investor_post",
            "message",
            "meeting_link",
            "preference",
        ]
