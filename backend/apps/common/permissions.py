from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.owner == request.user


class HasProjectAccess(permissions.BasePermission):
    """
    Permission to check if a user has access to a project.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # If there's a project_id in the URL, check access
        if hasattr(view, 'kwargs') and 'project_id' in view.kwargs:
            from apps.projects.models import Project
            try:
                project = Project.objects.get(
                    id=view.kwargs['project_id'],
                    owner=request.user,
                    is_active=True
                )
                # Store project in view for later use
                view.project = project
                return True
            except Project.DoesNotExist:
                return False
        
        return True