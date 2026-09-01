from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'company', 'bio', 'is_active', 'last_active_at',
            'date_joined'
        )
        read_only_fields = ('id', 'is_active', 'last_active_at', 'date_joined')
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ('email', 'password', 'password_confirm', 'first_name', 'last_name', 'company')
    
    def validate(self, attrs):
        """
        Check that the two password fields match.
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password_confirm": _("Password fields didn't match.")}
            )
        return attrs
    
    def create(self, validated_data):
        """
        Create and return a new user instance.
        """
        # Remove password_confirm from validated data
        validated_data.pop('password_confirm')
        
        # Create user
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            company=validated_data.get('company', ''),
        )
        
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """
        Validate the login credentials.
        """
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Authenticate user
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    _('Unable to log in with provided credentials.'),
                    code='authorization'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    _('User account is disabled.'),
                    code='authorization'
                )
            
            # Update last active
            user.update_last_active()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            attrs['user'] = user
            attrs['refresh'] = str(refresh)
            attrs['access'] = str(refresh.access_token)
            
            return attrs
        else:
            raise serializers.ValidationError(
                _('Must include "email" and "password".'),
                code='authorization'
            )


class LogoutSerializer(serializers.Serializer):
    """
    Serializer for user logout.
    """
    def validate(self, attrs):
        """
        Validate the logout request.
        """
        request = self.context.get('request')
        
        if not request or not request.user:
            raise serializers.ValidationError(
                _('You must be logged in to logout.'),
                code='authorization'
            )
        
        return attrs