import re
import hashlib
import json
import logging
from django.http import JsonResponse
from django.utils import timezone
from django.urls import resolve
from apps.api_keys.models import APIKey
from apps.projects.models import Project
from apps.gateway.models import ProjectAPIAssignment, APIDefinition

logger = logging.getLogger(__name__)


class APIKeyAuthenticationMiddleware:
    """
    Middleware to authenticate external API requests using API keys.
    """
    
    # List of paths that require API key authentication
    EXTERNAL_API_PATHS = [
        '/external/v1/',
        '/api/v1/',  # Alternative path
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Check if this is an external API request
        if self.is_external_api_request(request):
            # Authenticate the request
            auth_result = self.authenticate_request(request)
            
            if auth_result['authenticated']:
                # Store the API key and project in the request for later use
                request.api_key = auth_result['api_key']
                request.project = auth_result['project']
                request.api_key_id = auth_result['api_key'].id

                # Detect which API is being called
                request.api_definition = self.get_api_definition(request)
                
                # Check if the API is enabled for this project
                if not self.is_api_enabled(request):
                    return JsonResponse(
                        {
                            'error': 'APINotEnabled',
                            'detail': 'This API is not enabled for your project.',
                            'status_code': 403
                        },
                        status=403
                    )
                
                # Continue with the request
                response = self.get_response(request)
                
                # Log the request after processing
                self.log_request(request, response)
                
                return response
            else:
                # Authentication failed
                return JsonResponse(
                    {
                        'error': 'AuthenticationFailed',
                        'detail': auth_result['error'],
                        'status_code': 401
                    },
                    status=401
                )
        
        # Not an external API request, continue normally
        return self.get_response(request)
    
    def is_external_api_request(self, request):
        """
        Check if the request is to an external API endpoint.
        """
        path = request.path
        
        # Check if path matches any external API pattern
        for api_path in self.EXTERNAL_API_PATHS:
            if path.startswith(api_path):
                return True
        
        return False
    
    def authenticate_request(self, request):
        """
        Authenticate the request using the API key.
        """
        # Get the API key from the Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return {
                'authenticated': False,
                'error': 'Authorization header missing. Use: Authorization: Bearer YOUR_API_KEY'
            }
        
        # Parse the header
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return {
                'authenticated': False,
                'error': 'Invalid Authorization header format. Use: Bearer YOUR_API_KEY'
            }
        
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
            return {
                'authenticated': False,
                'error': 'Invalid or inactive API key.'
            }
        
        # Check if the key has expired
        if api_key_obj.is_expired:
            return {
                'authenticated': False,
                'error': 'API key has expired.'
            }
        
        # Get the project
        project = api_key_obj.project
        
        # Check if the project is active
        if not project.is_active:
            return {
                'authenticated': False,
                'error': 'Project is inactive.'
            }
        
        # Update last used timestamp
        api_key_obj.update_last_used()
        
        return {
            'authenticated': True,
            'api_key': api_key_obj,
            'project': project
        }
    
    def is_api_enabled(self, request):
        """
        Check if the requested API is enabled for the project.
        """
        path = request.path
        
        # Extract the API slug from the path
        # Example: /external/v1/weather/current -> weather-current
        # This is a simple mapping - you can make it more sophisticated
        
        # For now, let's do a simple check
        # Get all enabled APIs for the project
        enabled_apis = ProjectAPIAssignment.objects.filter(
            project=request.project,
            is_enabled=True
        ).select_related('api_definition')
        
        # Check if the requested path matches any enabled API
        # This is a simplified check - we'll improve it in the next iteration
        for assignment in enabled_apis:
            api_def = assignment.api_definition
            # Remove /external/v1/ from the path
            clean_path = path.replace('/external/v1/', '').replace('/api/v1/', '')
            
            # Check if the path matches the API definition path
            # Remove {id} patterns for matching
            api_path = api_def.path.replace('/v1/', '')
            # Convert {id} to a regex pattern
            import re
            pattern = re.sub(r'\{[^}]+\}', r'[^/]+', api_path)
            if re.match(f'^{pattern}$', clean_path):
                return True
        
        return False
    
    def log_request(self, request, response):
        """
        Log the API request for analytics.
        """
        # This will be implemented in Phase 2 with the RequestLog model
        # For now, just log to console
        logger.info(
            f"API Request: {request.method} {request.path} "
            f"Status: {response.status_code} "
            f"Project: {request.project.id} "
            f"API Key: {request.api_key_id}"
        )

    def get_api_definition(self, request):
        """Get the API definition for the requested endpoint."""
        path = request.path.replace('/external/v1/', '')

        try:
            # Try exact match first
            return APIDefinition.objects.get(
                path=f'/v1/{path}',
                method=request.method,
                is_active=True
            )
        except APIDefinition.DoesNotExist:
            # Try patterns matching for the paths with ID
            for api_def in APIDefinition.objects.filter(is_active=True):
                # Remove /v1/ fr0m API
                api_path = api_def.path.replace('/v1/', '')
                # Convert {id} to regex pattern
                pattern = re.sub(r'\{[^]+\}', r'[^/]+', api_path)
                if re.match(f'^{pattern}$', path):
                    return api_def

        return None         