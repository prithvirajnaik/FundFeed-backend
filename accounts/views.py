from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model

from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

User = get_user_model()


# -------------------------------
# HELPER: Generate JWT tokens
# -------------------------------
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


# -------------------------------
# POST /auth/register
# -------------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": tokens,
            },
            status=status.HTTP_201_CREATED,
        )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------
# POST /auth/login
# -------------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data["user"]
        tokens = get_tokens_for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------
# GET /auth/me
# -------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)
