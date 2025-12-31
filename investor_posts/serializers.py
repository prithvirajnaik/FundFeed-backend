from rest_framework import serializers
from .models import InvestorPost, SavedInvestorPost
from accounts.serializers import UserSerializer


class InvestorPostSerializer(serializers.ModelSerializer):
    investor = UserSerializer(read_only=True)

    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = InvestorPost
        fields = [
            "id",
            "investor",
            "title",
            "description",
            "tags",
            "stages",
            "amount_range",
            "location",
            "contact_preference",
            "logo_url",
            "views",
            "saved_count",
            "created_at",
        ]

    def get_logo_url(self, obj):
        if obj.logo:
            url = obj.logo.url
            # If it's already a full URL (Cloudinary), return as-is
            if url.startswith('http'):
                return url
            # Otherwise, build absolute URL for local /media/ paths
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

class InvestorPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorPost
        fields = [
            "title",
            "description",
            "tags",
            "stages",
            "amount_range",
            "location",
            "contact_preference",
            "logo",
        ]


class SavedInvestorPostSerializer(serializers.ModelSerializer):
    post = InvestorPostSerializer(read_only=True)

    class Meta:
        model = SavedInvestorPost
        fields = ["id", "developer", "post", "saved_at"]


