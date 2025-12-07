from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model

from .models import DeveloperProfile, InvestorProfile

User = get_user_model()


# ----------------------------
# USER SERIALIZER (for output)
# ----------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "role",
            "avatar_url",
            "location",
        ]


# ----------------------------
# REGISTER SERIALIZER
# ----------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "password", "role"]

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password"],
            role=validated_data["role"],
        )

        # Auto-create user profile
        if user.role == "developer":
            DeveloperProfile.objects.create(user=user)
        else:
            InvestorProfile.objects.create(user=user)

        return user


# ----------------------------
# LOGIN SERIALIZER
# ----------------------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        # Since USERNAME_FIELD = "email", authenticate using username=email
        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password")

        return {"user": user}
