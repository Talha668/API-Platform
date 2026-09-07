from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import exceptions


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that extracts the token from cookies.
    """
    
    def authenticate(self, request):
        """
        Extract the access token from the cookie.
        """
        # Try to get token from the cookie
        access_token = request.COOKIES.get(settings.JWT_ACCESS_COOKIE_NAME)
        
        if not access_token:
            # If no cookie, try Authorization header (for mobile clients, etc.)
            return super().authenticate(request)
        
        # Validate the token
        try:
            validated_token = AccessToken(access_token)
        except (InvalidToken, TokenError) as e:
            raise exceptions.AuthenticationFailed(str(e))
        
        # Get the user
        user = self.get_user(validated_token)
        return (user, validated_token)
    
    def get_user(self, validated_token):
        """
        Get the user from the validated token.
        """
        try:
            user_id = validated_token[settings.SIMPLE_JWT['USER_ID_CLAIM']]
        except KeyError:
            raise exceptions.AuthenticationFailed(
                'Token contained no recognizable user identification'
            )
        
        try:
            user = self.user_model.objects.get(**{
                settings.SIMPLE_JWT['USER_ID_FIELD']: user_id
            })
        except self.user_model.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')
        
        if not user.is_active:
            raise exceptions.AuthenticationFailed('User is inactive')
        
        return user


def set_jwt_cookies(response, access_token, refresh_token=None):
    """
    Helper function to set JWT cookies on the response.
    """
    # Set access token cookie
    response.set_cookie(
        key=settings.JWT_ACCESS_COOKIE_NAME,
        value=str(access_token),
        httponly=settings.JWT_COOKIE_HTTPONLY,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
    )
    
    # Set refresh token cookie if provided
    if refresh_token:
        response.set_cookie(
            key=settings.JWT_REFRESH_COOKIE_NAME,
            value=str(refresh_token),
            httponly=settings.JWT_COOKIE_HTTPONLY,
            secure=settings.JWT_COOKIE_SECURE,
            samesite=settings.JWT_COOKIE_SAMESITE,
            max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
        )
    
    return response


def clear_jwt_cookies(response):
    """
    Helper function to clear JWT cookies from the response.
    """
    response.delete_cookie(
        key=settings.JWT_ACCESS_COOKIE_NAME,
        path='/',
        samesite=settings.JWT_COOKIE_SAMESITE,
    )
    response.delete_cookie(
        key=settings.JWT_REFRESH_COOKIE_NAME,
        path='/',
        samesite=settings.JWT_COOKIE_SAMESITE,
    )
    return response