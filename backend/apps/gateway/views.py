from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.utils import timezone
from apps.projects.models import Project
from .models import APIDefinition, ProjectAPIAssignment
from .serializers import (
    APIDefinitionSerializer,
    ProjectAPIAssignmentSerializer,
    ProjectAPIEnableSerializer
)
from apps.common.permissions import HasProjectAccess
from .authentication import ExternalAPIAuthentication
from apps.common.permissions import HasProjectAccess






class APIDefinitionListView(generics.ListAPIView):
    """
    List all available API definitions that users can enable.
    """
    permission_classes = [permissions.IsAuthenticated]
    queryset = APIDefinition.objects.filter(is_active=True)
    serializer_class = APIDefinitionSerializer
    
    @extend_schema(
        responses={
            200: APIDefinitionSerializer(many=True),
            401: OpenApiResponse(description='Authentication required'),
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Get all available API definitions.
        """
        return super().get(request, *args, **kwargs)


class ProjectEnabledAPIsView(generics.ListAPIView):
    """
    List all APIs enabled for a specific project.
    """
    permission_classes = [permissions.IsAuthenticated, HasProjectAccess]
    serializer_class = ProjectAPIAssignmentSerializer
    
    def get_queryset(self):
        """Return enabled APIs for the project."""
        project_id = self.kwargs['project_id']
        return ProjectAPIAssignment.objects.filter(
            project_id=project_id,
            is_enabled=True
        ).select_related('api_definition')
    
    @extend_schema(
        responses={
            200: ProjectAPIAssignmentSerializer(many=True),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Project not found or access denied'),
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Get all enabled APIs for a project.
        """
        return super().get(request, *args, **kwargs)


class ProjectAPIEnableView(APIView):
    """
    Enable an API for a project.
    """
    permission_classes = [permissions.IsAuthenticated, HasProjectAccess]
    
    @extend_schema(
        request=ProjectAPIEnableSerializer,
        responses={
            200: ProjectAPIAssignmentSerializer,
            400: OpenApiResponse(description='Validation error'),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Project not found or access denied'),
            404: OpenApiResponse(description='API definition not found'),
        }
    )
    def post(self, request, project_id):
        """
        Enable an API for the project.
        """
        serializer = ProjectAPIEnableSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        api_slug = serializer.validated_data['api_slug']
        
        # Get the API definition
        try:
            api_def = APIDefinition.objects.get(slug=api_slug, is_active=True)
        except APIDefinition.DoesNotExist:
            return Response(
                {'detail': f'API with slug "{api_slug}" not found.'},
                status=404
            )
        
        # Get the project
        project = Project.objects.get(id=project_id, owner=request.user)
        
        # Create or update the assignment
        assignment, created = ProjectAPIAssignment.objects.get_or_create(
            project=project,
            api_definition=api_def,
            defaults={
                'is_enabled': True,
                'rate_limit': api_def.default_rate_limit
            }
        )
        
        if not created and not assignment.is_enabled:
            assignment.is_enabled = True
            assignment.save()
        
        # Serialize and return
        response_serializer = ProjectAPIAssignmentSerializer(assignment)
        return Response(response_serializer.data, status=200)


class ProjectAPIDisableView(APIView):
    """
    Disable an API for a project.
    """
    permission_classes = [permissions.IsAuthenticated, HasProjectAccess]
    
    @extend_schema(
        responses={
            204: OpenApiResponse(description='API disabled successfully'),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Project not found or access denied'),
            404: OpenApiResponse(description='API assignment not found'),
        }
    )
    def delete(self, request, project_id, api_slug):
        """
        Disable an API for the project.
        """
        # Get the API definition
        try:
            api_def = APIDefinition.objects.get(slug=api_slug)
        except APIDefinition.DoesNotExist:
            return Response(
                {'detail': f'API with slug "{api_slug}" not found.'},
                status=404
            )
        
        # Get the project
        project = Project.objects.get(id=project_id, owner=request.user)
        
        # Get the assignment
        try:
            assignment = ProjectAPIAssignment.objects.get(
                project=project,
                api_definition=api_def
            )
        except ProjectAPIAssignment.DoesNotExist:
            return Response(
                {'detail': 'API is not enabled for this project.'},
                status=404
            )
        
        # Disable the API
        assignment.is_enabled = False
        assignment.disabled_at = timezone.now()
        assignment.save()
        
        return Response(status=204)


class ExternalAPIBaseView(APIView):
    """
    Base view for external API endpoints.
    Uses API key authentication.
    """
    authentication_classes = [ExternalAPIAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]  # Will be handled by middleware
    
    def get_api_definition(self, request, **kwargs):
        """
        Get the API definition for the requested endpoint.
        """
        # Get the path without the /external/v1/ prefix
        path = request.path.replace('/external/v1/', '')
        
        # Build the full path pattern
        # Replace ID placeholders with actual values
        for key, value in kwargs.items():
            path = path.replace(value, f'{{{key}}}')
        
        # Look up the API definition
        try:
            return APIDefinition.objects.get(
                path=f'/v1/{path}',
                method=request.method
            )
        except APIDefinition.DoesNotExist:
            return None
    
    def get_mock_response(self, api_def, request, **kwargs):
        """
        Get the mock response for the API definition.
        """
        # You can add logic here to customize responses based on request parameters
        mock_data = api_def.mock_data
        
        # For list endpoints, you might want to filter or paginate
        if api_def.path == '/v1/tasks' and request.method == 'GET':
            # Add query parameter filtering
            status_filter = request.query_params.get('status')
            if status_filter and mock_data and 'results' in mock_data:
                filtered_results = [
                    task for task in mock_data['results']
                    if task.get('status') == status_filter
                ]
                mock_data['count'] = len(filtered_results)
                mock_data['results'] = filtered_results
        
        # For detail endpoints, use the ID from kwargs
        if '{id}' in api_def.path:
            # Return the first item for simplicity
            if mock_data and 'results' in mock_data and mock_data['results']:
                return mock_data['results'][0]
        
        return mock_data
    
    def handle_request(self, request, **kwargs):
        """
        Handle the external API request.
        """
        # Get the API definition
        api_def = self.get_api_definition(request, **kwargs)
        
        if not api_def:
            return Response(
                {
                    'error': 'NotFound',
                    'detail': 'API endpoint not found.'
                },
                status=404
            )
        
        # Check if the API is enabled for the project
        if hasattr(request, 'api_key'):
            try:
                assignment = ProjectAPIAssignment.objects.get(
                    project=request.api_key.project,
                    api_definition=api_def,
                    is_enabled=True
                )
            except ProjectAPIAssignment.DoesNotExist:
                return Response(
                    {
                        'error': 'APINotEnabled',
                        'detail': 'This API is not enabled for your project.'
                    },
                    status=403
                )
        
        # Get the mock response
        response_data = self.get_mock_response(api_def, request, **kwargs)
        
        # Add metadata to the response
        if isinstance(response_data, dict):
            response_data['_meta'] = {
                'api': api_def.name,
                'version': 'v1',
                'timestamp': timezone.now().isoformat(),
            }
        
        return Response(response_data)    


class WeatherCurrentView(ExternalAPIBaseView):
    def get(self, request):
        return self.handle_request(request)


class WeatherForecastView(ExternalAPIBaseView):
    def get(self, request):
        return self.handle_request(request)


class TaskListView(ExternalAPIBaseView):
    def get(self, request):
        return self.handle_request(request)

    def post(self, request):
        return self.handle_request(request)


class TaskDetailView(ExternalAPIBaseView):
    def get(self, request, id):
        return self.handle_request(request, id=id)

    def put(self, request, id):
        return self.handle_request(request, id=id)

    def delete(self, request, id):
        return self.handle_request(request, id=id)


class CurrencyListView(ExternalAPIBaseView):
    def get(self, request):
        return self.handle_request(request)


class ExchangeRateView(ExternalAPIBaseView):
    def get(self, request):
        return self.handle_request(request)                        