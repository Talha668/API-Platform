from rest_framework.views import exception_handler
from rest_framework import exceptions
from rest_framework.response import Response
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF that provides consistent error responses.
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the response format based on exception type
        if isinstance(exc, exceptions.ValidationError):
            response.data = {
                'error': 'ValidationError',
                'detail': 'Validation error occurred.',
                'errors': response.data,
                'status_code': response.status_code
            }
        elif isinstance(exc, exceptions.AuthenticationFailed):
            response.data = {
                'error': 'AuthenticationFailed',
                'detail': response.data.get('detail', 'Authentication failed.'),
                'status_code': response.status_code
            }
        elif isinstance(exc, exceptions.PermissionDenied):
            response.data = {
                'error': 'PermissionDenied',
                'detail': response.data.get('detail', 'You do not have permission.'),
                'status_code': response.status_code
            }
        elif isinstance(exc, exceptions.NotFound):
            response.data = {
                'error': 'NotFound',
                'detail': response.data.get('detail', 'The requested resource does not exist.'),
                'status_code': response.status_code
            }
        elif isinstance(exc, exceptions.MethodNotAllowed):
            response.data = {
                'error': 'MethodNotAllowed',
                'detail': response.data.get('detail', 'Method not allowed.'),
                'status_code': response.status_code
            }
        elif isinstance(exc, exceptions.Throttled):
            response.data = {
                'error': 'Throttled',
                'detail': response.data.get('detail', 'Request was throttled.'),
                'status_code': response.status_code
            }
        elif isinstance(exc, exceptions.ParseError):
            response.data = {
                'error': 'ParseError',
                'detail': response.data.get('detail', 'Malformed request.'),
                'status_code': response.status_code
            }
        elif isinstance(exc, IntegrityError):
            response = Response(
                {
                    'error': 'IntegrityError',
                    'detail': 'A database integrity error occurred.',
                    'status_code': 400
                },
                status=400
            )
        elif isinstance(exc, DjangoValidationError):
            response = Response(
                {
                    'error': 'ValidationError',
                    'detail': str(exc),
                    'status_code': 400
                },
                status=400
            )
    
    return response