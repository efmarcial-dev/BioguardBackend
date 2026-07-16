from rest_framework import serializers

from .models import Clinic, ClinicMembership, Profile


class ClinicSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Clinic
        fields = [
            "id", "name", "email", "phone_number",
            
            "address_line1", "address_line2", "city", "state",
            
            "country", "postal_code", "latitude", "longitude",
            
            "is_active", "created_at", "updated_at"
        ]
        
        read_only_fields = ["id", "created_at", "updated_at"]
        
class ClinicMembershipSerializer(serializers.ModelSerializer):
    
    clinic = ClinicSerializer(read_only=True)
    clinic_id = serializers.PrimaryKeyRelatedField(
        queryset = Clinic.objects.all(), source="clinic", write_only=True
    )
    
    class Meta:
        model = ClinicMembership
        fields = [
            "id", "clinic", "clinic_id", "role", "is_primary", "joined_at"
        ]
        
        
class ProfileSerializer(serializers.ModelSerializer):
    clinic_membership = ClinicMembershipSerializer(many=True, read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            "id", "firebase_uid", "email", "username", 
            "first_name", "last_name", "phone_number", "avatar_url",
            "is_active", "created_at", "updated_at", "clinic_membership"
        ]
        
        # Identify fields come from Firebase, not from client edits
        read_only_fields = ["id", "firebase_uid", "email", "is_active", "created_at", "updated_at"]
        