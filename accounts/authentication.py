import firebase_admin
from django.conf import settings
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials
from rest_framework import authentication, exceptions


from .models import Profile

# Initialize the Firebase Admin SDK exactly once per process.
if not firebase_admin._apps:
    # Build Firebase credentials from environment variables
    firebase_config = {
        "type": settings.FIREBASE_TYPE,
        "project_id": settings.FIREBASE_PROJECT_ID,
        "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
        "private_key": settings.FIREBASE_PRIVATE_KEY,
        "client_email": settings.FIREBASE_CLIENT_EMAIL,
        "client_id": settings.FIREBASE_CLIENT_ID,
        "auth_uri": settings.FIREBASE_AUTH_URI,
        "token_uri": settings.FIREBASE_TOKEN_URI,
        "auth_provider_x509_cert_url": settings.FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
        "client_x509_cert_url": settings.FIREBASE_CLIENT_X509_CERT_URL,
        "universe_domain": settings.FIREBASE_UNIVERSE_DOMAIN,
    }
    try:
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Failed Firebase auth admin: {e}")

else:
    print("Nothing is happining ")
    
class FirebaseAuthentication(authentication.BaseAuthentication):
    
    """
    Expects: Authorization: Bearer <Firebase ID token>
    
    
    On success request.user is set to the local `Profile` row matching the 
    token's 'uid' (creating a bare-bones one on first sigth), and
    request.auth is set to the decoded token dict (uid, email, claims, ...)
    """
    
    keyword = "Bearer"
    
    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).decode("utf-8")
        if not auth_header:
            return None    
    
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            return None
        
        id_token = parts[1]
        
        try:
            decoded_token = firebase_auth.verify_id_token(id_token, check_revoked=True)
        except firebase_auth.ExpiredIdTokenError:
            raise exceptions.AuthenticationFailed("Firebase token has expired")
        except firebase_auth.RevokedIdTokenError:
            raise exceptions.AuthenticationFailed("Firebase token has been revoked")
        except Exception:
            raise exceptions.AuthenticationFailed("Invalid Firebase token.")
        
        firebase_uid = decoded_token.get('uid')
        email = decoded_token.get("email", "")
        
        
        profile, _ = Profile.objects.get_or_create(
            firebase_uid=firebase_uid,
            defaults={"email": email}
        )
        
        if not profile.is_active:
            raise exceptions.AuthenticationFailed("This account has been disbaled")
        
        # Keep email in sync in case it changed on the Firebase side.
        if email and profile.email != email:
            profile.email = email
            profile.save(update_fields=["email"])
            
        return (profile, decoded_token)
    
    def authenticate_header(self, request):
        return self.keyword