import logging
from django.http import JsonResponse
from django.utils import timezone
from .services import TieredRateLimiter

logger = logging.getLogger(__name__)





class RateLimitMiddleware:
    """
    Middleware to enforce rate limits on API requests.
    """
    
    # Skip rate limiting for these paths
    SKIP_PATHS = [
        '/api/auth/login',
        '/api/auth/register',
        '/api/auth/refresh',
        '/api/auth/logout',
        '/api/schema',
        '/api/docs',
        '/admin',
        '/static',
        '/media',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limiter = TieredRateLimiter()
    
    def __call__(self, request):
        # Skip rate limiting for certain paths
        if self.should_skip_ratelimit(request):
            return self.get_response(request)
        
        # Only apply rate limiting to external API requests
        if self.is_external_api_request(request):
            # Get identifier (API key or IP)
            identifier = self.get_identifier(request)
            
            # Get tier from project or default to free
            tier = self.get_project_tier(request)
            
            # Get API definition if available
            api_definition = getattr(request, 'api_definition', None)
            
            # Check rate limit
            is_limited, response_data = self.rate_limiter.check_rate_limit(
                identifier=identifier,
                tier=tier,
                api_definition=api_definition
            )
            
            # Add rate limit headers to response
            if is_limited:
                # Return 429 Too Many Requests
                response = JsonResponse(
                    {
                        'error': 'RateLimitExceeded',
                        'detail': response_data.get('detail', 'Rate limit exceeded.'),
                        'limit': response_data.get('limit', 0),
                        'remaining': 0,
                        'reset': response_data.get('reset', 0),
                        'retry_after': response_data.get('retry_after', 0),
                    },
                    status=429
                )
                
                # Add retry-after header
                retry_after = response_data.get('retry_after', 3600)
                response['Retry-After'] = str(retry_after)
                response['X-RateLimit-Limit'] = str(response_data.get('limit', 0))
                response['X-RateLimit-Remaining'] = '0'
                response['X-RateLimit-Reset'] = str(response_data.get('reset', 0))
                
                # Log rate limit exceeded
                logger.warning(
                    f"Rate limit exceeded for {identifier} on {request.path} "
                    f"(Tier: {tier}, Limit: {response_data.get('limit', 0)})"
                )
                
                return response
            
            # Process the request
            response = self.get_response(request)
            
            # Add rate limit headers to successful response
            if hasattr(response, 'status_code') and response.status_code < 400:
                response['X-RateLimit-Limit'] = str(response_data.get('limit', 0))
                response['X-RateLimit-Remaining'] = str(response_data.get('remaining', 0))
                response['X-RateLimit-Reset'] = str(response_data.get('reset', 0))
            
            return response
        
        # Not an external API request, continue normally
        return self.get_response(request)
    
    def should_skip_ratelimit(self, request):
        """Check if rate limiting should be skipped."""
        path = request.path
        
        for skip_path in self.SKIP_PATHS:
            if path.startswith(skip_path):
                return True
        
        # Skip for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return True
        
        return False
    
    def is_external_api_request(self, request):
        """Check if the request is to an external API endpoint."""
        path = request.path
        
        # Check if path matches external API patterns
        external_patterns = ['/external/v1/', '/api/v1/']
        for pattern in external_patterns:
            if path.startswith(pattern):
                return True
        
        return False
    
    def get_identifier(self, request):
        """Get a unique identifier for rate limiting."""
        # Use API key if available
        if hasattr(request, 'api_key') and request.api_key:
            return f"key_{request.api_key.id}"
        
        # Use project if available
        if hasattr(request, 'project') and request.project:
            return f"project_{request.project.id}"
        
        # Fallback to IP address
        return f"ip_{self.get_client_ip(request)}"
    
    def get_project_tier(self, request):
        """Get the project tier for rate limiting."""
        if hasattr(request, 'project') and request.project:
            # Check if project has tier attribute
            if hasattr(request.project, 'tier'):
                return request.project.tier
            
            # Check if project is from a paid user
            if hasattr(request.project, 'owner') and request.project.owner:
                # Check if user is pro or enterprise
                if hasattr(request.project.owner, 'subscription_tier'):
                    return request.project.owner.subscription_tier
        
        # Default to free
        return 'free'
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.headers.get('X-Forwarded-For')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip