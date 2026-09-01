from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.projects.models import Project
from .models import APIKey
from .serializers import (
    APIKeySerializer, APIKeyCreateSerializer, APIKeyUpdateSerializer
)


class APIKeyListCreateView(generics.ListCreateAPIView):
    """
    List all API keys for a project, or create a new API key.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return API keys belonging to the current user's project."""
        project_id = self.kwargs['project_id']
        
        # Verify the user owns the project
        project = Project.objects.get(id=project_id, owner=self.request.user)
        
        return APIKey.objects.filter(
            project=project
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on request method."""
        if self.request.method == 'POST':
            return APIKeyCreateSerializer
        return APIKeySerializer
    
    def get_serializer_context(self):
        """Add the project to the serializer context."""
        context = super().get_serializer_context()
        project_id = self.kwargs['project_id']
        project = Project.objects.get(id=project_id, owner=self.request.user)
        context['project'] = project
        return context
    
    @extend_schema(
        responses={
            200: APIKeySerializer(many=True),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Project not found or access denied'),
        }
    )
    def get(self, request, *args, **kwargs):
        """
        List all API keys for a project.
        """
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        request=APIKeyCreateSerializer,
        responses={
            201: APIKeySerializer,
            400: OpenApiResponse(description='Validation error'),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Project not found or access denied'),
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Create a new API key for a project.
        """
        return super().post(request, *args, **kwargs)


class APIKeyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete (revoke) an API key.
    """
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        """Return API keys belonging to the current user's project."""
        project_id = self.kwargs['project_id']
        
        # Verify the user owns the project
        Project.objects.get(id=project_id, owner=self.request.user)
        
        return APIKey.objects.filter(
            project_id=project_id
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on request method."""
        if self.request.method in ['PUT', 'PATCH']:
            return APIKeyUpdateSerializer
        return APIKeySerializer
    
    @extend_schema(
        responses={
            200: APIKeySerializer,
            404: OpenApiResponse(description='API key not found'),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Project not found or access denied'),
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieve a specific API key.
        """
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        request=APIKeyUpdateSerializer,
        responses={
            200: APIKeySerializer,
            400: OpenApiResponse(description='Validation error'),
            404: OpenApiResponse(description='API key not found'),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Project not found or access denied'),
        }
    )
    def put(self, request, *args, **kwargs):
        """
        Update a specific API key.
        """
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        request=APIKeyUpdateSerializer,
        responses={
            200: APIKeySerializer,
            400: OpenApiResponse(description='Validation error'),
            404: OpenApiResponse(description='API key not found'),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Project not found or access denied'),
        }
    )
    def patch(self, request, *args, **kwargs):
        """
        Partially update a specific API key.
        """
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        responses={
            204: OpenApiResponse(description='API key revoked successfully'),
            404: OpenApiResponse(description='API key not found'),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Project not found or access denied'),
        }
    )
    def delete(self, request, *args, **kwargs):
        """
        Revoke (soft delete) a specific API key.
        """
        instance = self.get_object()
        instance.revoke()
        return Response(status=status.HTTP_204_NO_CONTENT)


class APIKeyRegenerateView(generics.GenericAPIView):
    """
    Regenerate an API key (rotate the secret).
    """
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        """Return API keys belonging to the current user's project."""
        project_id = self.kwargs['project_id']
        
        # Verify the user owns the project
        Project.objects.get(id=project_id, owner=self.request.user)
        
        return APIKey.objects.filter(
            project_id=project_id,
            is_active=True
        )
    
    @extend_schema(
        responses={
            200: APIKeySerializer,
            404: OpenApiResponse(description='API key not found'),
            401: OpenApiResponse(description='Authentication required'),
            403: OpenApiResponse(description='Project not found or access denied'),
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Regenerate a specific API key.
        """
        instance = self.get_object()
        
        # Regenerate the key
        full_key = instance.regenerate()
        
        # Store the full key temporarily for the response
        instance._temp_key = full_key
        
        # Serialize the response
        serializer = APIKeySerializer(instance)
        
        return Response(serializer.data, status=status.HTTP_200_OK)