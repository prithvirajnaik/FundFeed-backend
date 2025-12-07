from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvestorPostViewSet

router = DefaultRouter()
router.register(r"investor-posts", InvestorPostViewSet, basename="investor-posts")

urlpatterns = [
    path("", include(router.urls)),
]
