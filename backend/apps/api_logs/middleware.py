import time
import logging
from django.utils import timezone
from .models import RequestLog

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """
    Middleware to log all API requests for analytics.
    """
    
    # List of paths to skip logging
    SKIP_PATHS = [
        '/api/auth/login',
        '/api/auth/refresh',
        '/api/auth/register',
        '/api/schema',
        '/api/docs',
        '/admin',
        '/static',
        '/media',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip logging for certain paths
        if self.should_skip_logging(request):
            return self.get_response(request)
        
        # Start timing
        start_time = time.time()
        
        # Store request data before processing
        request_data = {
            'method': request.method,
            'path': request.path,
            'full_url': request.build_absolute_uri(),
            'ip': RequestLog.get_client_ip(request),
            'user_agent': request.headers.get('User-Agent', ''),
        }
        
        # Process the request
        try:
            response = self.get_response(request)
            status_code = response.status_code
            error_message = ''
        except Exception as e:
            # If an exception occurs, create a response with error details
            status_code = 500
            error_message = str(e)
            response = None
            raise  # Re-raise the exception after logging
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log the request asynchronously (or synchronously for now)
        try:
            # Get project and API key from request
            project = None
            api_key = None
            api_definition = None
            
            if hasattr(request, 'project'):
                project = request.project
            elif hasattr(request, 'api_key'):
                api_key = request.api_key
                project = api_key.project
            
            # Get API definition if available
            if hasattr(request, 'api_definition'):
                api_definition = request.api_definition
            
            # Create log entry
            log = RequestLog.objects.create(
                project=project,
                api_key=api_key,
                api_definition=api_definition,
                method=request_data['method'],
                path=request_data['path'],
                full_url=request_data['full_url'],
                status_code=status_code,
                response_time=response_time_ms,
                ip_address=request_data['ip'],
                user_agent=request_data['user_agent'],
                is_error=status_code >= 400,
                error_message=error_message,
                is_authenticated=api_key is not None,
                created_at=timezone.now()
            )
            
            logger.debug(f"Logged request: {log.method} {log.path} - {log.status_code} ({log.response_time}ms)")
            
        except Exception as e:
            # Don't let logging errors affect the response
            logger.error(f"Failed to log request: {str(e)}")
        
        return response
    
    def should_skip_logging(self, request):
        """Check if logging should be skipped for this request."""
        path = request.path
        
        # Skip logging for static assets and health checks
        for skip_path in self.SKIP_PATHS:
            if path.startswith(skip_path):
                return True
        
        # Skip logging for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return True
        
        return False