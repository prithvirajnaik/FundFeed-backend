from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import User, DeveloperProfile, InvestorProfile
from .serializers import UserSerializer
from .profile_serializers import (
    DeveloperProfileSerializer,
    InvestorProfileSerializer,
)


# -----------------------------------------------------
# GET /profile/<user_id>/  → public profile
# -----------------------------------------------------
@api_view(["GET"])
@permission_classes([AllowAny])
def public_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)

    user_data = UserSerializer(user, context={"request": request}).data

    if user.role == "developer":
        profile = DeveloperProfile.objects.filter(user=user).first()
        profile_data = DeveloperProfileSerializer(
            profile, context={"request": request}
        ).data if profile else None

    else:  # investor
        profile = InvestorProfile.objects.filter(user=user).first()
        profile_data = InvestorProfileSerializer(
            profile, context={"request": request}
        ).data if profile else None

    return Response({
        "user": user_data,
        "profile": profile_data,
    })

# -----------------------------------------------------
# PATCH /profile/update/
# -----------------------------------------------------
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user

    if user.role == "developer":
        profile, _ = DeveloperProfile.objects.get_or_create(user=user)
        serializer = DeveloperProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={"request": request}
        )

    else:
        profile, _ = InvestorProfile.objects.get_or_create(user=user)
        serializer = InvestorProfileSerializer(
            profile,
            data=request.data,
            partial=True,
            context={"request": request}
        )

    if serializer.is_valid():
        serializer.save()
        return Response({"profile": serializer.data})

    return Response(serializer.errors, status=400)
