from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PitchViewSet, SavePitchView, SavedListView

router = DefaultRouter()
router.register(r"pitches", PitchViewSet, basename="pitches")

urlpatterns = [

    # Saved list
    path("pitches/saved/", SavedListView.as_view({"get": "list"})),
    # Save / Unsave
    path("pitches/<str:pitch_id>/save/", SavePitchView.as_view({"post": "create"})),
    path("pitches/<str:pitch_id>/unsave/", SavePitchView.as_view({"delete": "destroy"})),

    path("", include(router.urls)),
]
