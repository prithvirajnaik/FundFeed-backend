from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import InvestorPost, SavedInvestorPost
from .serializers import (
    InvestorPostSerializer,
    InvestorPostCreateSerializer,
    SavedInvestorPostSerializer,
)

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
    queryset = InvestorPost.objects.all().order_by("-created_at")
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "description", "tags", "stages", "location"]

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
