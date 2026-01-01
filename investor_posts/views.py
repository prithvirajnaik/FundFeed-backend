from rest_framework import viewsets, permissions, status, filters
from django.http import HttpResponse
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import InvestorPost, SavedInvestorPost
from .serializers import (
    InvestorPostSerializer,
    InvestorPostCreateSerializer,
    SavedInvestorPostSerializer,
)

from django.core.mail import send_mail
from django.conf import settings
class IsInvestorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow investors to create posts.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'investor'

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.investor == request.user

class InvestorPostViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        from django.db.models import Q
        queryset = InvestorPost.objects.all().order_by("-created_at")

        # 1. Investor Filter (Dashboard)
        investor_id = self.request.query_params.get('investor')
        if investor_id:
            if investor_id == 'me':
                queryset = queryset.filter(investor=self.request.user)
            else:
                queryset = queryset.filter(investor__id=investor_id)

        # 1. Search (Title, Description, Location)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )

        # 2. Tags Filter (JSONField)
        tag = self.request.query_params.get('tags')
        if tag:
            queryset = queryset.filter(tags__icontains=tag)

        # 3. Stage Filter (JSONField)
        stage = self.request.query_params.get('stage')
        if stage:
            queryset = queryset.filter(stages__icontains=stage)

        # 4. Location Filter
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)

        return queryset

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return InvestorPostCreateSerializer
        return InvestorPostSerializer

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsInvestorOrReadOnly]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(investor=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def save(self, request, pk=None):
        post = self.get_object()
        user = request.user
        
        # Only developers usually save investor posts, but let's allow any auth user for now
        if SavedInvestorPost.objects.filter(developer=user, post=post).exists():
            return Response({"detail": "Already saved."}, status=status.HTTP_200_OK)

        SavedInvestorPost.objects.create(developer=user, post=post)
        post.saved_count += 1
        post.save()
        return Response({"detail": "Post saved."}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], permission_classes=[permissions.IsAuthenticated])
    def unsave(self, request, pk=None):
        post = self.get_object()
        user = request.user

        saved_post = SavedInvestorPost.objects.filter(developer=user, post=post).first()
        if not saved_post:
            return Response({"detail": "Not saved."}, status=status.HTTP_400_BAD_REQUEST)

        saved_post.delete()
        post.saved_count -= 1
        post.save()
        return Response({"detail": "Post unsaved."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def saved(self, request):
        user = request.user
        saved_posts = SavedInvestorPost.objects.filter(developer=user).select_related("post")
        serializer = SavedInvestorPostSerializer(saved_posts, many=True)
        return Response(serializer.data)





@api_view(['GET'])
@permission_classes([AllowAny])
def test(request):
    """
    Test endpoint to verify email sending configuration.
    Usage: /api/test/?email=target@example.com
    """
    target_email = request.GET.get('email', 'prithvirajnaik318@gmail.com')
    
    # If authenticated, try to use user's email if no param provided
    if not request.GET.get('email') and request.user.is_authenticated:
        target_email = request.user.email

    try:
        print("EMAIL_BACKEND IN USE:", settings.EMAIL_BACKEND)
        print("FROM EMAIL:", settings.DEFAULT_FROM_EMAIL)
        print("SMTP USER:", settings.EMAIL_HOST_USER)

        print(f"************* Sending Test Email to {target_email} ***************")
        send_mail(
            subject="Test Email from FundFeed",
            message="This is a test email to verify the notification system is working correctly.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[target_email],
            fail_silently=False,
        )
        print("************* Email Sent Successfully ***************")
        return HttpResponse(f"Email sent successfully to {target_email}", status=200)
    except Exception as e:
        print(f"************* Email Failed: {str(e)} ***************")
        return HttpResponse(f"Failed to send email: {str(e)}", status=500)