from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from apps.projects.models import Project
from apps.common.permissions import HasProjectAccess
from .models import RequestLog, AggregatedMetric
from .serializers import RequestLogSerializer, AggregatedMetricSerializer
from .services import AnalyticsService




class RequestLogListView(generics.ListAPIView):
    """
    List request logs for a project with filtering.
    """
    permission_classes = [permissions.IsAuthenticated, HasProjectAccess]
    serializer_class = RequestLogSerializer
    
    def get_queryset(self):
        """Return request logs for the project."""
        project_id = self.kwargs['project_id']
        queryset = RequestLog.objects.filter(
            project_id=project_id
        ).select_related('api_key', 'api_definition')
        
        # Apply filters
        status_code = self.request.query_params.get('status_code')
        if status_code:
            queryset = queryset.filter(status_code=status_code)
        
        api_slug = self.request.query_params.get('api')
        if api_slug:
            queryset = queryset.filter(api_definition__slug=api_slug)
        
        method = self.request.query_params.get('method')
        if method:
            queryset = queryset.filter(method=method.upper())
        
        # Date range filters
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset.order_by('-created_at')
    
    @extend_schema(
        parameters=[
            {
                'name': 'status_code',
                'description': 'Filter by HTTP status code',
                'required': False,
                'schema': {'type': 'integer'}
            },
            {
                'name': 'api',
                'description': 'Filter by API slug',
                'required': False,
                'schema': {'type': 'string'}
            },
            {
                'name': 'method',
                'description': 'Filter by HTTP method',
                'required': False,
                'schema': {'type': 'string', 'enum': ['GET', 'POST', 'PUT', 'DELETE']}
            },
            {
                'name': 'start_date',
                'description': 'Filter by start date (ISO format)',
                'required': False,
                'schema': {'type': 'string', 'format': 'date-time'}
            },
            {
                'name': 'end_date',
                'description': 'Filter by end date (ISO format)',
                'required': False,
                'schema': {'type': 'string', 'format': 'date-time'}
            },
        ],
        responses={
            200: RequestLogSerializer(many=True),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Project not found or access denied'),
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Get request logs with optional filters.
        """
        return super().get(request, *args, **kwargs)


class ProjectAnalyticsView(APIView):
    """
    Get analytics for a project.
    """
    permission_classes = [permissions.IsAuthenticated, HasProjectAccess]
    
    @extend_schema(
        responses={
            200: OpenApiResponse(description='Analytics data'),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Project not found or access denied'),
        }
    )
    def get(self, request, project_id):
        """
        Get analytics for a project.
        """
        days = int(request.query_params.get('days', 7))
        
        # Validate days parameter
        if days > 90:
            days = 90
        
        analytics = AnalyticsService.get_project_analytics(project_id, days=days)
        return Response(analytics)


class APIAnalyticsView(APIView):
    """
    Get analytics for a specific API within a project.
    """
    permission_classes = [permissions.IsAuthenticated, HasProjectAccess]
    
    @extend_schema(
        responses={
            200: OpenApiResponse(description='API analytics data'),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Project not found or access denied'),
            404: OpenApiResponse(description='API not found or not enabled'),
        }
    )
    def get(self, request, project_id, api_slug):
        """
        Get analytics for a specific API.
        """
        from apps.gateway.models import APIDefinition, ProjectAPIAssignment
        
        # Verify the API exists and is enabled for the project
        try:
            api_def = APIDefinition.objects.get(slug=api_slug, is_active=True)
            
            # Check if the API is enabled for this project
            ProjectAPIAssignment.objects.get(
                project_id=project_id,
                api_definition=api_def,
                is_enabled=True
            )
        except (APIDefinition.DoesNotExist, ProjectAPIAssignment.DoesNotExist):
            return Response(
                {
                    'error': 'APINotFound',
                    'detail': f'API "{api_slug}" is not available or not enabled for this project.'
                },
                status=404
            )
        
        days = int(request.query_params.get('days', 7))
        if days > 90:
            days = 90
        
        analytics = AnalyticsService.get_api_analytics(project_id, api_def.id, days=days)
        return Response(analytics)