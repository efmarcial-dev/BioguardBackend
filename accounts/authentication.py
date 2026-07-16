from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from firebase_admin import auth
from django.contrib.auth.models import User

from .models import Profile


class FirebaseAuthentication(BaseAuthentication):
    
    """
    Expects: Authorization: Bearer <Firebase ID token>
    
    
    On success request.user is set to the local `Profile` row matching the 
    token's 'uid' (creating a bare-bones one on first sigth), and
    request.auth is set to the decoded token dict (uid, email, claims, ...)
    """
    
    keyword = "Bearer"
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None    # No credentials provided; pass to other authentication schemes
    
    
        # Parse the 'Bearer <token>' pattern
        try:
            auth_type, id_token = auth_header.split(' ')
            if auth_type.lower() != 'bearer':
                raise AuthenticationFailed("Authorization header must start with Bearer")
        except ValueError:
            raise AuthenticationFailed("Invalid authorization header format")
        
        
        try:
            # Verify the token against Firebase servers using the ADMIN SDK
            decoded_token = auth.verify_id_token(id_token)
        except Exception as e:
            print(f"DEBUG: Firebase Token Verification Faild: {e}")
            raise AuthenticationFailed(f'Invalid Firebase Token: {str(e)}')
        
        firebase_uid = decoded_token.get('uid')
        email = decoded_token.get("email", "")
        
        print(f"AUTH TYPE: {auth_type}")
        print(f"Firebase ID Token: {id_token}")
        print(f'Firebase UID: {firebase_uid}')
        print(f"Firebase Email: {email}")
        
        
        # Map to and existing Django user or create a new local shell user
        user, created = User.objects.get_or_create(
            username=firebase_uid, # Use unique Firebase UID as the unique Django username
            defaults={'email': email}
        )
        
        profile, _ = Profile.objects.get_or_create(
            firebase_uid=firebase_uid,
            defaults={"email": email}
        )
        
        if not profile.is_active:
            raise AuthenticationFailed("This account has been disbaled")
        
        # Keep email in sync in case it changed on the Firebase side.
        if email and profile.email != email:
            profile.email = email
            profile.save(update_fields=["email"])
            
        return (profile, decoded_token)
    
    def authenticate_header(self, request):
        return self.keyword