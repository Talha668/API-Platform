from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Project(models.Model):
    """
    Model representing a user's API project.
    Each project can have multiple API keys and endpoints.
    """
    name = models.CharField(_('project name'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name=_('owner')
    )
    
    # Project settings
    is_active = models.BooleanField(_('active'), default=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    deleted_at = models.DateTimeField(_('deleted at'), blank=True, null=True)
    
    class Meta:
        db_table = 'projects'
        verbose_name = _('project')
        verbose_name_plural = _('projects')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def soft_delete(self):
        """Soft delete the project."""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_active', 'deleted_at'])
    
    @property
    def total_requests(self):
        """Get the total number of requests for this project."""
        from apps.api_keys.models import APIKey
        from apps.gateway.models import RequestLog  # Will be created in Phase 2
        
        # This will be implemented in Phase 2
        return 0
    
    @property
    def api_keys_count(self):
        """Get the number of active API keys for this project."""
        return self.api_keys.filter(is_active=True).count()