from django.urls import path
from .views import register, login, me
from .views_profile import public_profile, update_profile


urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login, name="login"),
    path("me/", me, name="me"),
    path("profile/<str:user_id>/", public_profile),
    path("profile/update/", update_profile, name="update_profile"),

]


