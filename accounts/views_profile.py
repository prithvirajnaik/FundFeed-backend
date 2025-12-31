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
@api_view(["PATCH", "OPTIONS"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user

    # Handle Avatar Upload
    if "avatar" in request.FILES:
        avatar_file = request.FILES["avatar"]
        print(f"[DEBUG] Received avatar file: {avatar_file.name}, size: {avatar_file.size}")
        
        try:
            import cloudinary.uploader
            print("[DEBUG] Cloudinary module imported successfully")
            
            # Upload directly to Cloudinary
            result = cloudinary.uploader.upload(
                avatar_file,
                folder="avatars",
                public_id=f"{user.id}_{avatar_file.name.split('.')[0]}",
                overwrite=True,
                resource_type="image"
            )
            print(f"[DEBUG] Cloudinary result: {result}")
            
            # Get the secure URL from Cloudinary response
            user.avatar_url = result.get('secure_url') or result.get('url')
            print(f"[DEBUG] Saved avatar_url: {user.avatar_url}")
            user.save()
        except Exception as e:
            print(f"[ERROR] Cloudinary upload failed: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: save locally if Cloudinary fails
            from django.core.files.storage import default_storage
            from django.core.files.base import ContentFile
            file_path = default_storage.save(f"avatars/{user.id}_{avatar_file.name}", ContentFile(avatar_file.read()))
            user.avatar_url = f"/media/{file_path}"
            user.save()
    else:
        print(f"[DEBUG] No avatar in request.FILES. Keys: {list(request.FILES.keys())}")

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
        # Return updated user data as well to reflect new avatar
        return Response({
            "profile": serializer.data,
            "avatar_url": user.avatar_url
        })

    return Response(serializer.errors, status=400)
