from rest_framework import serializers
from .models import DeveloperProfile, InvestorProfile
from .serializers import UserSerializer   # import from above


# ----------------------------
# DEVELOPER PROFILE
# ----------------------------
class DeveloperProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = DeveloperProfile
        fields = "__all__"


# ----------------------------
# INVESTOR PROFILE
# ----------------------------
class InvestorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = InvestorProfile
        fields = "__all__"
