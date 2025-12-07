from rest_framework import serializers
from .models import Pitch, SavedPitch
from accounts.serializers import UserSerializer


# ---------------------------------------------------
# PITCH SERIALIZER (list + detail)
# ---------------------------------------------------
class PitchSerializer(serializers.ModelSerializer):
    developer = UserSerializer(read_only=True)

    video_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    saves = serializers.SerializerMethodField()     # ⭐ NEW FIELD

    class Meta:
        model = Pitch
        fields = [
            "id",
            "developer",
            "title",
            "description",
            "tags",
            "funding_stage",
            "ask",
            "video_url",
            "thumbnail_url",
            "views",
            "saves",          # ⭐ ADDED HERE
            "created_at",
        ]

    # ---------------------------------------------
    # Absolute video URL
    # ---------------------------------------------
    def get_video_url(self, obj):
        if obj.video:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.video.url)
        return None

    # ---------------------------------------------
    # Absolute thumbnail URL
    # ---------------------------------------------
    def get_thumbnail_url(self, obj):
        if obj.thumbnail:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.thumbnail.url)
        return None

    # ---------------------------------------------
    # Count saves
    # ---------------------------------------------
    def get_saves(self, obj):
        return obj.savedpitch_set.count()


# ---------------------------------------------------
# PITCH CREATE SERIALIZER
# ---------------------------------------------------
class PitchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pitch
        fields = [
            "title",
            "description",
            "tags",
            "funding_stage",
            "ask",
            "video",
            "thumbnail",
        ]


# ---------------------------------------------------
# SAVED PITCH SERIALIZER
# ---------------------------------------------------
class SavedPitchSerializer(serializers.ModelSerializer):
    pitch = PitchSerializer(read_only=True)

    class Meta:
        model = SavedPitch
        fields = ["id", "investor", "pitch", "saved_at"]
