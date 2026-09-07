from rest_framework import serializers
from .models import Project
from apps.common.choices import SubscriptionTier


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Project model.
    """
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    api_keys_count = serializers.IntegerField(read_only=True)
    enabled_apis_count = serializers.IntegerField(read_only=True)
    
    # Request statistics
    total_requests = serializers.IntegerField(read_only=True)
    successful_requests = serializers.IntegerField(read_only=True)
    failed_requests = serializers.IntegerField(read_only=True)
    error_rate = serializers.FloatField(read_only=True)
    avg_response_time = serializers.FloatField(read_only=True)
    
    # Rate limiting
    rate_limit = serializers.IntegerField(read_only=True)
    rate_limit_daily = serializers.IntegerField(read_only=True)
    rate_limit_remaining = serializers.IntegerField(read_only=True)
    
    # Usage summary
    total_requests_today = serializers.IntegerField(read_only=True)
    total_requests_this_week = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Project
        fields = (
            'id', 'name', 'description', 'owner', 'owner_email',
            'is_active', 'tier', 'custom_rate_limit',
            'api_keys_count', 'enabled_apis_count',
            'total_requests', 'successful_requests', 'failed_requests',
            'error_rate', 'avg_response_time',
            'rate_limit', 'rate_limit_daily', 'rate_limit_remaining',
            'total_requests_today', 'total_requests_this_week',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'owner', 'created_at', 'updated_at',
            'api_keys_count', 'enabled_apis_count',
            'total_requests', 'successful_requests', 'failed_requests',
            'error_rate', 'avg_response_time',
            'rate_limit', 'rate_limit_daily', 'rate_limit_remaining',
            'total_requests_today', 'total_requests_this_week'
        )


class ProjectCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new project.
    """
    class Meta:
        model = Project
        fields = ('name', 'description', 'tier', 'custom_rate_limit')
    
    def validate_name(self, value):
        """
        Validate that the project name is not empty.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Project name cannot be empty.")
        return value.strip()

    def validate_custom_rate_limit(self, value):
        """
        Validate custom rate limit.
        """
        if value is not None and value < 1:
            raise serializers.ValidationError("Rate limit must be at least 1.")
        return value
    
    def create(self, validated_data):
        """
        Create a new project with the current user as owner.
        """
        request = self.context.get('request')
        user = request.user
        
        project = Project.objects.create(
            owner=user,
            name=validated_data['name'],
            description=validated_data.get('description', ''),
            tier=validated_data.get('tier', SubscriptionTier.FREE),
            custom_rate_limit=validated_data.get('custom_rate_limit'),
        )
        
        return project


class ProjectUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a project.
    """
    class Meta:
        model = Project
        fields = ('name', 'description', 'is_active', 'tier', 'custom_rate_limit')
    
    def validate_name(self, value):
        """
        Validate that the project name is not empty.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Project name cannot be empty.")
        return value.strip()

    def validate_custom_rate_limit(self, value):
        """
        Validate custom rate limit.
        """
        if value is not None and value < 1:
            raise serializers.ValidationError("Rate limit must at least 1.")
        return value


class ProjectUsageSerializer(serializers.Serializer):
    """
    Serializer for project usage statistics.
    """    
    daily_stats = serializers.ListField(child=serializers.DictField())
    top_endpoints = serializers.ListField(child=serializers.DictField())
    status_distribution = serializers.DictField()
    summary = serializers.DictField()