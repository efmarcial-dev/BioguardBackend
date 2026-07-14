from django.contrib import admin
from .models import *


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "first_name", "last_name", "is_active", "created_at")
    search_fields = ("email", "username", "firebase_uid", "first_name", "last_name")
    list_filter = ("is_active",)
    
@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "city", "country", "is_active")
    search_fields = ("name", "email", "city")
    list_filter = ("is_active", "country")
    
@admin.register(ClinicMembership)
class ClinicMemebershipAdmin(admin.ModelAdmin):
    list_display = ("profile", "clinic", "role", "is_primary", "joined_at")
    list_filter = ("role", "is_primary")