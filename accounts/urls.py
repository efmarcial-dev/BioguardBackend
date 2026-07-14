from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"clinics", ClinicViewSet, basename="clinic")

urlpatterns = [
    path('user-profile/', UserProfile.as_view , name="user-profile"),
    path("profile/me/", MeView.as_view(), name="profile-me"),
    path("" ,include(router.urls)),
]
