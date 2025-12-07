from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Pitch, SavedPitch
from .serializers import (
    PitchSerializer, 
    PitchCreateSerializer,
    SavedPitchSerializer
)


# -----------------------------------------------------
# PITCH VIEWSET
# -----------------------------------------------------
class PitchViewSet(viewsets.ModelViewSet):
    queryset = Pitch.objects.all().order_by("-created_at")
    serializer_class = PitchSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return PitchCreateSerializer
        return PitchSerializer

    # ⭐ IMPORTANT FIX
    def create(self, request, *args, **kwargs):
        create_serializer = PitchCreateSerializer(data=request.data)
        create_serializer.is_valid(raise_exception=True)

        pitch = create_serializer.save(developer=request.user)

        # Return full pitch, not partial
        output_serializer = PitchSerializer(pitch, context={"request": request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def add_view(self, request, pk=None):
        pitch = self.get_object()
        pitch.views += 1
        pitch.save()
        return Response({"views": pitch.views})


# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

class SavePitchView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, pitch_id=None):
        user = request.user

        # Make sure the pitch exists — avoid implicit 404 inside get_or_create
        pitch = get_object_or_404(Pitch, id=pitch_id)

        saved, created = SavedPitch.objects.get_or_create(
            investor=user,
            pitch=pitch
        )
        serializer = SavedPitchSerializer(saved, context={"request": request})

        # Idempotent: always return 200/201 but not a 400
        if not created:
            return Response({"detail": "Already saved", "saved": True}, status=status.HTTP_200_OK)

        # return the saved object (optionally)
        # serializer = SavedPitchSerializer(saved)
        return Response({"detail": "Saved", "saved": True, "item": serializer.data}, status=status.HTTP_201_CREATED)

    def destroy(self, request, pitch_id=None):
        user = request.user
        pitch = get_object_or_404(Pitch, id=pitch_id)

        try:
            obj = SavedPitch.objects.get(investor=user, pitch=pitch)
            obj.delete()
            return Response({"detail": "Removed", "saved": False}, status=status.HTTP_200_OK)
        except SavedPitch.DoesNotExist:
            return Response({"detail": "Not saved", "saved": False}, status=status.HTTP_200_OK)

# -----------------------------------------------------
# GET SAVED LIST
# /pitches/saved/
# -----------------------------------------------------
class SavedListView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        saved = SavedPitch.objects.filter(investor=user)
        serializer = SavedPitchSerializer(saved, many=True, context={"request": request})
        return Response(serializer.data)
