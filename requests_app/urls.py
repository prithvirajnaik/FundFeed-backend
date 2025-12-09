from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactRequestViewSet

router = DefaultRouter()
router.register(r"requests", ContactRequestViewSet, basename="contact-requests")

urlpatterns = [
    path("", include(router.urls)),
]
