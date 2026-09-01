from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class APICategory(models.Model):
    """
    Category for grouping related APIs.
    """
    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True, null=True)
    icon = models.CharField(_('icon'), max_length=50, blank=True, null=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'api_categories'
        verbose_name = _('API category')
        verbose_name_plural = _('API categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class APIDefinition(models.Model):
    """
    Predefined API definitions that users can enable for their projects.
    """
    class HttpMethod(models.TextChoices):
        GET = 'GET', 'GET'
        POST = 'POST', 'POST'
        PUT = 'PUT', 'PUT'
        PATCH = 'PATCH', 'PATCH'
        DELETE = 'DELETE', 'DELETE'
    
    name = models.CharField(_('API name'), max_length=100)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True, null=True)
    
    # API endpoint details
    path = models.CharField(_('endpoint path'), max_length=255)
    method = models.CharField(
        _('HTTP method'),
        max_length=10,
        choices=HttpMethod.choices,
        default=HttpMethod.GET
    )
    
    # API metadata
    category = models.ForeignKey(
        APICategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='apis',
        verbose_name=_('category')
    )
    
    # Additional settings
    requires_auth = models.BooleanField(_('requires authentication'), default=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    # Rate limiting (can be overridden per project)
    default_rate_limit = models.IntegerField(_('default rate limit per hour'), default=100)
    
    # Mock data or handler
    response_schema = models.JSONField(
        _('response schema'),
        blank=True,
        null=True,
        help_text='JSON schema for the response'
    )
    mock_data = models.JSONField(
        _('mock data'),
        blank=True,
        null=True,
        help_text='Mock data to return for this endpoint'
    )
    
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'api_definitions'
        verbose_name = _('API definition')
        verbose_name_plural = _('API definitions')
        ordering = ['category', 'name']
        unique_together = [['path', 'method']]
    
    def __str__(self):
        return f"{self.method} {self.path} - {self.name}"


class ProjectAPIAssignment(models.Model):
    """
    Link between a project and an API definition, representing an enabled API.
    """
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='enabled_apis',
        verbose_name=_('project')
    )
    api_definition = models.ForeignKey(
        APIDefinition,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name=_('API definition')
    )
    
    # Custom rate limit override
    rate_limit = models.IntegerField(
        _('rate limit per hour'),
        null=True,
        blank=True,
        help_text='Override the default rate limit for this API'
    )
    
    # Status
    is_enabled = models.BooleanField(_('enabled'), default=True)
    
    # Timestamps
    enabled_at = models.DateTimeField(_('enabled at'), default=timezone.now)
    disabled_at = models.DateTimeField(_('disabled at'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    
    class Meta:
        db_table = 'project_api_assignments'
        verbose_name = _('project API assignment')
        verbose_name_plural = _('project API assignments')
        unique_together = [['project', 'api_definition']]
        indexes = [
            models.Index(fields=['project', 'is_enabled']),
        ]
    
    def __str__(self):
        return f"{self.project.name} - {self.api_definition.name} ({'Enabled' if self.is_enabled else 'Disabled'})"