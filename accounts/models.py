from django.db import models

class Profile(models.Model):
    """
    A local record for a firebase-authenticated user.
    Django/Supabase never stores password - Firebase owns credentials.
    This row is created automatically (see FirebaseAuthentication) the 
    first time is verified Firebase user hits the API, then fille in via
    PATCH /api/profile/me/.
    """
    
    firebase_uid = models.CharField(max_length=128, unique=True, db_index=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=32, blank=True)
    avatar_url = models.URLField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # --- Required so DRF permission classes (IsAuthenticated, etc)..
    # can treat a Profile instance like a "user" ---
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def __str__(self):
        return self.username or self.email
    
    
class Clinic(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=32, blank=True)
    
    
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longtitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name 
    

class ClinicMembership(models.Model):
    """ Which profile works at which clinic, and in what capacity """
    
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("admin", "Admin"),
        ("doctor", "Doctor"),
        ("staff", "Staff")
    ]
    
    profile = models.ForeignKey(
        Profile, related_name="clinic_memberships", on_delete=models.CASCADE
    )
    
    clinic = models.ForeignKey(
        Clinic, related_name="memberships", on_delete=models.CASCADE
    )
    
    role = models.CharField(choices=ROLE_CHOICES, max_length=32, default="staff")
    is_primary = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['profile', 'clinic'], name="unique_profile_clinic"
            )
        ]
        
        
    def __str__(self):
        return f"{self.profile} @ {self.clinic} ({self.role})"