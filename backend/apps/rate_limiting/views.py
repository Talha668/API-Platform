from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.common.permissions import HasProjectAccess
from .services import TieredRateLimiter





class RateLimitStatusView(APIView):
    """
    View to check current rate limit usage.
    """
    permission_classes = [permissions.IsAuthenticated, HasProjectAccess]
    
    def get(self, request, project_id):
        """
        Get current rate limit usage for the project.
        """
        # Get the project
        from apps.projects.models import Project
        try:
            project = Project.objects.get(id=project_id, owner=request.user)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=404
            )
        
        # Get tier from project or user
        tier = project.tier if hasattr(project, 'tier') else request.user.subscription_tier
        
        # Get identifier
        identifier = f"project_{project_id}"
        
        # Get usage
        rate_limiter = TieredRateLimiter()
        usage = rate_limiter.get_usage(identifier, tier)
        
        # Add additional info
        usage['project'] = project.name
        usage['api_keys_count'] = project.api_keys.filter(is_active=True).count()
        
        return Response(usage)


class RateLimitResetView(APIView):
    """
    View to reset rate limit usage (admin only).
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, project_id):
        """
        Reset rate limit for a project.
        """
        # Check if user is admin or superuser
        if not request.user.is_staff and not request.user.is_superuser:
            return Response(
                {'error': 'Permission denied'},
                status=403
            )
        
        from apps.projects.models import Project
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=404
            )
        
        # Reset rate limits
        rate_limiter = RateLimiter()
        identifier = f"project_{project_id}"
        
        # Reset both hourly and daily limits
        rate_limiter.reset_usage(identifier, 'default:hourly')
        rate_limiter.reset_usage(identifier, 'default:daily')
        
        # Reset API-specific limits
        from apps.gateway.models import APIDefinition
        for api_def in APIDefinition.objects.filter(is_active=True):
            rate_limiter.reset_usage(identifier, f"{api_def.slug}:hourly")
            rate_limiter.reset_usage(identifier, f"{api_def.slug}:daily")
        
        return Response({
            'message': f'Rate limits reset for project "{project.name}"',
            'project_id': project_id
        })