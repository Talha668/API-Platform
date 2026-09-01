from rest_framework import serializers
from .models import APICategory, APIDefinition, ProjectAPIAssignment


class APICategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = APICategory
        fields = ('id', 'name', 'slug', 'description', 'icon')


class APIDefinitionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    
    class Meta:
        model = APIDefinition
        fields = (
            'id', 'name', 'slug', 'description',
            'path', 'method', 'category', 'category_name', 'category_slug',
            'requires_auth', 'default_rate_limit',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class ProjectAPIAssignmentSerializer(serializers.ModelSerializer):
    api_definition = APIDefinitionSerializer(read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    effective_rate_limit = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectAPIAssignment
        fields = (
            'id', 'project', 'project_name',
            'api_definition', 'rate_limit', 'effective_rate_limit',
            'is_enabled', 'enabled_at', 'disabled_at'
        )
        read_only_fields = ('id', 'project', 'enabled_at', 'disabled_at')
    
    def get_effective_rate_limit(self, obj):
        """Return the effective rate limit (custom or default)."""
        if obj.rate_limit is not None:
            return obj.rate_limit
        return obj.api_definition.default_rate_limit


class ProjectAPIEnableSerializer(serializers.Serializer):
    api_slug = serializers.SlugField()
    rate_limit = serializers.IntegerField(required=False, min_value=1)