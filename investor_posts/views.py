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
