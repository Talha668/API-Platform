from rest_framework import serializers
from .models import RequestLog, AggregatedMetric
from apps.api_keys.serializers import APIKeySerializer




class RequestLogSerializer(serializers.ModelSerializer):
    """
    Serializer for RequestLog model.
    """
    api_key_name = serializers.CharField(source='api_key.name', read_only=True, allow_null=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    api_name = serializers.CharField(source='api_definition.name', read_only=True, allow_null=True)
    api_slug = serializers.CharField(source='api_definition.slug', read_only=True, allow_null=True)
    
    class Meta:
        model = RequestLog
        fields = (
            'id', 'project', 'project_name',
            'api_key', 'api_key_name',
            'api_definition', 'api_name', 'api_slug',
            'method', 'path', 'full_url',
            'status_code', 'response_time',
            'ip_address', 'user_agent',
            'is_error', 'is_authenticated',
            'error_message',
            'created_at', 'processed_at'
        )
        read_only_fields = fields


class AggregatedMetricSerializer(serializers.ModelSerializer):
    """
    Serializer for AggregatedMetric model.
    """
    project_name = serializers.CharField(source='project.name', read_only=True)
    api_name = serializers.CharField(source='api_definition.name', read_only=True, allow_null=True)
    
    class Meta:
        model = AggregatedMetric
        fields = (
            'id', 'project', 'project_name',
            'api_definition', 'api_name',
            'metric_type', 'period_start', 'period_end',
            'total_requests', 'successful_requests', 'failed_requests',
            'avg_response_time', 'min_response_time', 'max_response_time',
            'status_code_distribution',
            'created_at', 'updated_at'
        )
        read_only_fields = fields