from rest_framework import serializers
from .models import APIKey


class APIKeySerializer(serializers.ModelSerializer):
    """
    Serializer for the APIKey model.
    """
    project_name = serializers.CharField(source='project.name', read_only=True)
    scope_display = serializers.CharField(source='get_scope_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    key = serializers.SerializerMethodField()
    
    class Meta:
        model = APIKey
        fields = (
            'id', 'name', 'project', 'project_name',
            'key', 'key_prefix', 'scope', 'scope_display',
            'is_active', 'is_expired',
            'last_used_at', 'expires_at',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'key', 'key_prefix', 'last_used_at', 
            'created_at', 'updated_at', 'is_expired'
        )
    
    def get_key(self, obj):
        """
        Return the full key if available, else None.
        This is used only when the key is created.
        """
        # This will be populated by the create view
        return getattr(obj, '_temp_key', None)


class APIKeyCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new API key.
    """
    class Meta:
        model = APIKey
        fields = ('name', 'scope', 'expires_at')
    
    def validate_name(self, value):
        """
        Validate that the key name is not empty.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Key name cannot be empty.")
        return value.strip()
    
    def create(self, validated_data):
        """
        Create a new API key with secure generation.
        """
        # Generate the API key
        full_key, prefix, key_hash = APIKey.generate_key()
        
        # Create the key instance
        key = APIKey.objects.create(
            project=self.context['project'],
            name=validated_data['name'],
            key_prefix=prefix,
            key_hash=key_hash,
            scope=validated_data.get('scope', APIKey.Scope.READ),
            expires_at=validated_data.get('expires_at'),
        )
        
        # Store the full key temporarily for the response
        key._temp_key = full_key
        
        return key


class APIKeyUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an API key.
    """
    class Meta:
        model = APIKey
        fields = ('name', 'scope', 'is_active')
    
    def validate_name(self, value):
        """
        Validate that the key name is not empty.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Key name cannot be empty.")
        return value.strip()