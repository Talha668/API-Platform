from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import hashlib
from apps.api_keys.models import APIKey


class ExternalAPIAuthentication(BaseAuthentication):
    """
    Authentication class for external API requests.
    """
    
    def authenticate(self, request):
        """
        Authenticate the request using the API key from the Authorization header.
        """
        # Get the API key from the Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return None
        
        # Parse the header
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        api_key = parts[1]
        
        # Hash the provided key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Look up the key in the database
        try:
            api_key_obj = APIKey.objects.get(
                key_hash=key_hash,
                is_active=True
            )
        except APIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid or inactive API key.')
        
        # Check if the key has expired
        if api_key_obj.is_expired:
            raise AuthenticationFailed('API key has expired.')
        
        # Check if the project is active
        if not api_key_obj.project.is_active:
            raise AuthenticationFailed('Project is inactive.')
        
        # Update last used timestamp
        api_key_obj.update_last_used()
        
        # Return the user (None for external API) and the auth token
        # We'll use the API key object as the auth token
        return (None, api_key_obj)
    
    def authenticate_header(self, request):
        """
        Return the authentication header for 401 responses.
        """
        return 'Bearer realm="API"'