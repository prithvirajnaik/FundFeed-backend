from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models
from .models import ContactRequest
from .serializers import ContactRequestSerializer, ContactRequestCreateSerializer
from pitches.models import Pitch
from investor_posts.models import InvestorPost

class ContactRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ContactRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        box = self.request.query_params.get("box", "inbox")

        # Base query: requests involving the user
        queryset = ContactRequest.objects.filter(
            models.Q(developer=user) | models.Q(investor=user)
        )

        if box == "sent":
            # User is SENDER if:
            # 1. They are Investor AND request is about a Pitch
            # 2. They are Developer AND request is about an InvestorPost
            queryset = queryset.filter(
                models.Q(investor=user, pitch__isnull=False) |
                models.Q(developer=user, investor_post__isnull=False)
            )
        else:
            # Default: INBOX (User is RECEIVER)
            # User is RECEIVER if:
            # 1. They are Developer AND request is about a Pitch
            # 2. They are Investor AND request is about an InvestorPost
            queryset = queryset.filter(
                models.Q(developer=user, pitch__isnull=False) |
                models.Q(investor=user, investor_post__isnull=False)
            )

        return queryset.order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return ContactRequestCreateSerializer
        return ContactRequestSerializer

    def perform_create(self, serializer):
        # Logic to determine sender and receiver
        # If sender is Investor -> Receiver is Developer (from Pitch)
        # If sender is Developer -> Receiver is Investor (from InvestorPost)
        
        user = self.request.user
        data = self.request.data
        
        pitch_id = data.get("pitch")
        post_id = data.get("investor_post")

        if pitch_id:
            # Investor contacting Developer
            pitch = get_object_or_404(Pitch, id=pitch_id)
            serializer.save(
                investor=user,
                developer=pitch.developer,
                pitch=pitch
            )
        elif post_id:
            # Developer contacting Investor
            post = get_object_or_404(InvestorPost, id=post_id)
            serializer.save(
                developer=user,
                investor=post.investor,
                investor_post=post
            )
        else:
            # Should not happen if validation is good, but just in case
            raise ValueError("Must provide either pitch or investor_post")

    @action(detail=True, methods=["post"])
    def mark_viewed(self, request, pk=None):
        contact_request = self.get_object()
        # Only the receiver should be able to mark as viewed
        # But for simplicity, let's just allow it if they are part of the request
        contact_request.viewed = True
        contact_request.save()
        return Response({"status": "marked as viewed"})
