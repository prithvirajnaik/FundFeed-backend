from rest_framework import serializers
from .models import ContactRequest, MeetingSummary
from accounts.serializers import UserSerializer
from pitches.serializers import PitchSerializer
from investor_posts.serializers import InvestorPostSerializer


class MeetingSummarySerializer(serializers.ModelSerializer):
    """Serializer for structured meeting summaries"""
    class Meta:
        model = MeetingSummary
        fields = [
            'id',
            'discussion_points',
            'action_items',
            'decisions_made',
            'next_steps',
            'needs_followup',
            'followup_date',
            'additional_notes',
            'created_at',
            'updated_at',
        ]


class ContactRequestSerializer(serializers.ModelSerializer):
    developer = UserSerializer(read_only=True)
    investor = UserSerializer(read_only=True)

    pitch = PitchSerializer(read_only=True)
    investor_post = InvestorPostSerializer(read_only=True)

    structured_summary = MeetingSummarySerializer(read_only=True)
    
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
            "scheduled_start_time",
            "scheduled_end_time",
            "meeting_status",
            "meeting_summary",
            "meeting_started_at",
            "meeting_ended_at",
            "timezone",
            "meeting_platform",
            "agenda",
            "structured_summary",
        ]


# -----------------------------------------------------
# For creating requests (developer → investor or vice-versa)
# -----------------------------------------------------
class ContactRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactRequest
        fields = [
            "pitch",
            "investor_post",
            "message",
            "meeting_link",
            "preference",
            "scheduled_start_time",
            "scheduled_end_time",
            "timezone",
            "meeting_platform",
            "agenda",
        ]
