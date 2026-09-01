from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Project
from .serializers import (
    ProjectSerializer, ProjectCreateSerializer, ProjectUpdateSerializer,
    ProjectUsageSerializer
)




class ProjectListCreateView(generics.ListCreateAPIView):
    """
    List all projects for the current user, or create a new project.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return projects belonging to the current user."""
        return Project.objects.filter(
            owner=self.request.user,
            is_active=True
        ).select_related('owner')
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on request method."""
        if self.request.method == 'POST':
            return ProjectCreateSerializer
        return ProjectSerializer

    def get_serializer_context(self):
        """
        Add request to context for creating projects.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @extend_schema(
        responses={
            200: ProjectSerializer(many=True),
            401: OpenApiResponse(description='Authentication required'),
        }
    )
    def get(self, request, *args, **kwargs):
        """
        List all projects for the current user.
        """
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        request=ProjectCreateSerializer,
        responses={
            201: ProjectSerializer,
            400: OpenApiResponse(description='Validation error'),
            401: OpenApiResponse(description='Authentication required'),
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Create a new project.
        """
        return super().post(request, *args, **kwargs)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a project.
    """
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        """Return projects belonging to the current user."""
        return Project.objects.filter(owner=self.request.user).select_related('owner')
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on request method."""
        if self.request.method in ['PUT', 'PATCH']:
            return ProjectUpdateSerializer
        return ProjectSerializer
    
    @extend_schema(
        responses={
            200: ProjectSerializer,
            404: OpenApiResponse(description='Project not found'),
            401: OpenApiResponse(description='Authentication required'),
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieve a specific project.
        """
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        request=ProjectUpdateSerializer,
        responses={
            200: ProjectSerializer,
            400: OpenApiResponse(description='Validation error'),
            404: OpenApiResponse(description='Project not found'),
            401: OpenApiResponse(description='Authentication required'),
        }
    )
    def put(self, request, *args, **kwargs):
        """
        Update a specific project.
        """
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        request=ProjectUpdateSerializer,
        responses={
            200: ProjectSerializer,
            400: OpenApiResponse(description='Validation error'),
            404: OpenApiResponse(description='Project not found'),
            401: OpenApiResponse(description='Authentication required'),
        }
    )
    def patch(self, request, *args, **kwargs):
        """
        Partially update a specific project.
        """
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        responses={
            204: OpenApiResponse(description='Project deleted successfully'),
            404: OpenApiResponse(description='Project not found'),
            401: OpenApiResponse(description='Authentication required'),
        }
    )
    def delete(self, request, *args, **kwargs):
        """
        Soft delete a specific project.
        """
        instance = self.get_object()
        instance.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectUsageView(APIView):
    """
    Get usage statistics for a project.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, id):
        """
        Get usage statistics for a project.
        """
        try:
            project = Project.objects.get(id=id, owner=request.user)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        days = int(request.query_params.get('days', 7))
        if days > 90:
            days = 90
        
        usage_stats = project.get_usage_stats(days=days)
        serializer = ProjectUsageSerializer(usage_stats)
        return Response(serializer.data)


class ProjectRateLimitView(APIView):
    """
    Get rate limit information for a project.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, id):
        """
        Get rate limit information for a project.
        """
        try:
            project = Project.objects.get(id=id, owner=request.user)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        usage = project.get_rate_limit_usage()
        return Response({
            'project_id': project.id,
            'project_name': project.name,
            'tier': project.tier,
            'rate_limit': project.rate_limit,
            'rate_limit_daily': project.rate_limit_daily,
            'usage': usage,
            'custom_rate_limit': project.custom_rate_limit,
        })    