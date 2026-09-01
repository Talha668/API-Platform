from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer, LogoutSerializer
)
from .authentication import set_jwt_cookies, clear_jwt_cookies


class RegisterView(generics.CreateAPIView):
    """
    Register a new user account.
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        responses={
            201: UserSerializer,
            400: OpenApiResponse(description='Validation error'),
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Register a new user.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Serialize user data
        user_serializer = UserSerializer(user)
        
        return Response(
            user_serializer.data,
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    """
    Login a user and set JWT cookies.
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        request=LoginSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description='Invalid credentials'),
            401: OpenApiResponse(description='Authentication failed'),
        }
    )
    def post(self, request):
        """
        Login user and set JWT cookies.
        """
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        access_token = serializer.validated_data['access']
        refresh_token = serializer.validated_data['refresh']
        
        # Serialize user data
        user_serializer = UserSerializer(user)
        
        # Create response
        response = Response(user_serializer.data, status=status.HTTP_200_OK)
        
        # Set JWT cookies
        set_jwt_cookies(response, access_token, refresh_token)
        
        return response


class LogoutView(APIView):
    """
    Logout a user and clear JWT cookies.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        request=LogoutSerializer,
        responses={
            204: OpenApiResponse(description='Successfully logged out'),
            401: OpenApiResponse(description='Authentication required'),
        }
    )
    def post(self, request):
        """
        Logout user and clear cookies.
        """
        serializer = LogoutSerializer(data={}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Blacklist the refresh token if needed
        # This is optional but adds extra security
        try:
            refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            # If token is invalid or blacklist not enabled, continue
            pass
        
        # Create response
        response = Response(status=status.HTTP_204_NO_CONTENT)
        
        # Clear JWT cookies
        clear_jwt_cookies(response)
        
        return response


class RefreshTokenView(APIView):
    """
    Refresh the access token using the refresh token cookie.
    """
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        responses={
            200: OpenApiResponse(description='Token refreshed successfully'),
            401: OpenApiResponse(description='Invalid or missing refresh token'),
        }
    )
    def post(self, request):
        """
        Refresh the access token.
        """
        # Get refresh token from cookie
        refresh_token = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)
        
        if not refresh_token:
            return Response(
                {'detail': _('Refresh token not found in cookies.')},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            # Validate refresh token
            token = RefreshToken(refresh_token)
            
            # Get the access token
            access_token = str(token.access_token)
            
            # Create response
            response = Response(
                {'detail': _('Token refreshed successfully.')},
                status=status.HTTP_200_OK
            )
            
            # Set new access token cookie
            response.set_cookie(
                key=settings.JWT_ACCESS_COOKIE_NAME,
                value=access_token,
                httponly=settings.JWT_COOKIE_HTTPONLY,
                secure=settings.JWT_COOKIE_SECURE,
                samesite=settings.JWT_COOKIE_SAMESITE,
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
            )
            
            return response
            
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """
    Get and update the current user's profile.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """
        Return the current user.
        """
        return self.request.user
    
    @extend_schema(
        responses={
            200: UserSerializer,
            401: OpenApiResponse(description='Authentication required'),
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Get current user profile.
        """
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description='Validation error'),
            401: OpenApiResponse(description='Authentication required'),
        }
    )
    def patch(self, request, *args, **kwargs):
        """
        Update current user profile.
        """
        return super().patch(request, *args, **kwargs)