from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics, permissions, viewsets
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from .serializers import *


@method_decorator(ratelimit(key="ip", rate='5/m', method="POST"), name="dispatch")
class UserProfile(APIView):
    
    permission_classes=[AllowAny]
    
    def post(self, request):
        
        return Response(
            {"Successful connection": True},
            status=status.HTTP_200_OK
        )
        


class MeView(generics.RetrieveUpdateAPIView):
    """
    GET /api/profile/me/ -> the caller's own profile (auto-created on first login)
    PATCH/PUT /api/profile/me -> update name, username, phone, avatar, etc.
    """
    
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self, request):
        # FirebaseAuthentication already put the matching Profile on request.user
        return self.request.user
    
    
class ClinicViewSet(viewsets.ModelViewSet):
    """
    Standart CRUD for clients
    GET/POST /api/clinics/
    GET/PATCH/DELETE/ /api/clinics/{id}/
    
    Lock this down further with real permissions classes (e.g. only "owner"/"admin"
    memberships can edit) before going live - IsAuthenticated alone just means
    "any verified Firebase user".
    """
    
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    permission_classes = [IsAuthenticated]
    