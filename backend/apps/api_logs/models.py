from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _




class RequestLog(models.Model):
    """
    Log of all APIs requests for analytics and monitoring.
    """

    # Relationship to project and API key
    project = models.ForeignKey('projects.Project', on_delete=models.SET_NULL, null=True, blank=True, related_name='request_logs', verbose_name='Project')
    api_key = models.ForeignKey('api_keys.APIKey', on_delete=models.SET_NULL, null=True, related_name='request_logs', verbose_name='API Key')

    # API details
    api_definition = models.ForeignKey('gateway.APIDefinition', on_delete=models.SET_NULL, null=True, related_name='request_logs', verbose_name='API definition')

    # Request details
    method = models.CharField(_('HTTP method'), max_length=10)
    path = models.CharField(_('endpoint path'), max_length=500)
    full_url = models.URLField(_('full URL'), max_length=1000, blank=True, null=True)

    # Response detail
    status_code = models.IntegerField(_('status code'), db_index=True)
    response_time = models.IntegerField(_('response time (ms)'), db_index=True)

    # Request metadata
    ip_address = models.GenericIPAddressField(_('IP address'), db_index=True)
    user_agent = models.TextField(_('user agent'), blank=True, null=True)

    # Request/response payloads (for debuggings)
    request_body = models.JSONField(_('request body'), blank=True, null=True)
    response_body = models.JSONField(_('response body'), blank=True, null=True)

    # Additional context
    error_message = models.TextField(_('error message'), blank=True, null=True)
    is_error = models.BooleanField(_('is error'), default=False, db_index=True)
    is_authenticated = models.BooleanField(_('is authenticated'), default=True)

    # Timestamps
    created_at = models.DateTimeField(_('created at'), default=timezone.now, db_index=True)
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)

    class Meta:
        db_table = 'request_logs'
        verbose_name = _('request log')
        verbose_name_plural = _('request logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'created_at']),
            models.Index(fields=['api_key', 'created_at']),
            models.Index(fields=['status_code', 'created_at']),
            models.Index(fields=['project', 'api_definition', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.path} - {self.status_code} ({self.created_at})"
    
    @classmethod
    def log_request(cls, request, response, response_time_ms, **kwargs):
        """
        Create a log entry for a request.
        """
        # Get the API definition if available
        api_def = None
        if hasattr(request, 'api_definition'):
            api_def = request.api_definition
        
        # Get the API key
        api_key = None
        project = None
        if hasattr(request, 'api_key'):
            api_key = request.api_key
            project = api_key.project
        
        # Create the log entry
        log = cls.objects.create(
            project=project or kwargs.get('project'),
            api_key=api_key,
            api_definition=api_def or kwargs.get('api_definition'),
            method=request.method,
            path=request.path,
            full_url=request.build_absolute_uri(),
            status_code=response.status_code,
            response_time=response_time_ms,
            ip_address=cls.get_client_ip(request),
            user_agent=request.headers.get('User-Agent', ''),
            request_body=cls.get_request_body(request),
            response_body=cls.get_response_body(response),
            is_error=response.status_code >= 400,
            is_authenticated=api_key is not None,
            error_message=kwargs.get('error_message', ''),
            processed_at=timezone.now()
        )
        
        return log
    
    @staticmethod
    def get_client_ip(request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.headers.get('X-Forwarded-For')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip
    
    @staticmethod
    def get_request_body(request):
        """Get the request body as JSON."""
        try:
            if request.body:
                return request.data if hasattr(request, 'data') else None
        except Exception:
            pass
        return None
    
    @staticmethod
    def get_response_body(response):
        """Get the response body as JSON."""
        try:
            if hasattr(response, 'data'):
                return response.data
            elif hasattr(response, 'content'):
                import json
                try:
                    return json.loads(response.content)
                except:
                    return None
        except Exception:
            pass
        return None


class AggregatedMetric(models.Model):
    """
    Aggregated metrics for analytics.
    Populated by Celery tasks to improve performance.
    """
    
    class MetricType(models.TextChoices):
        HOURLY = 'hourly', 'Hourly'
        DAILY = 'daily', 'Daily'
        MONTHLY = 'monthly', 'Monthly'
    
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='metrics',
        verbose_name=_('project')
    )
    api_definition = models.ForeignKey(
        'gateway.APIDefinition',
        on_delete=models.SET_NULL,
        null=True,
        related_name='metrics',
        verbose_name=_('API definition')
    )
    
    metric_type = models.CharField(
        _('metric type'),
        max_length=10,
        choices=MetricType.choices,
        db_index=True
    )
    period_start = models.DateTimeField(_('period start'), db_index=True)
    period_end = models.DateTimeField(_('period end'), db_index=True)
    
    # Counts
    total_requests = models.IntegerField(_('total requests'), default=0)
    successful_requests = models.IntegerField(_('successful requests'), default=0)
    failed_requests = models.IntegerField(_('failed requests'), default=0)
    
    # Response time metrics
    avg_response_time = models.FloatField(_('average response time'), default=0.0)
    min_response_time = models.IntegerField(_('minimum response time'), default=0)
    max_response_time = models.IntegerField(_('maximum response time'), default=0)
    
    # Status code distribution (stored as JSON)
    status_code_distribution = models.JSONField(
        _('status code distribution'),
        default=dict
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'aggregated_metrics'
        verbose_name = _('aggregated metric')
        verbose_name_plural = _('aggregated metrics')
        ordering = ['-period_start']
        unique_together = [['project', 'api_definition', 'metric_type', 'period_start']]
        indexes = [
            models.Index(fields=['project', 'metric_type', 'period_start']),
            models.Index(fields=['api_definition', 'period_start']),
        ]
    
    def __str__(self):
        return f"{self.project.name} - {self.metric_type} ({self.period_start})"
    
    @classmethod
    def aggregate_hourly(cls, hour_start):
        """
        Aggregate request logs for a specific hour.
        """
        from django.db.models import Count, Avg, Min, Max, Q
        
        hour_end = hour_start + timezone.timedelta(hours=1)
        
        # Get all logs for this hour
        logs = RequestLog.objects.filter(
            created_at__gte=hour_start,
            created_at__lt=hour_end
        )
        
        # Group by project and API definition
        results = logs.values('project', 'api_definition').annotate(
            total=Count('id'),
            successful=Count('id', filter=Q(status_code__lt=400)),
            failed=Count('id', filter=Q(status_code__gte=400)),
            avg_time=Avg('response_time'),
            min_time=Min('response_time'),
            max_time=Max('response_time'),
        )
        
        # Create or update metrics
        for result in results:
            metric, created = cls.objects.update_or_create(
                project_id=result['project'],
                api_definition_id=result['api_definition'],
                metric_type=cls.MetricType.HOURLY,
                period_start=hour_start,
                defaults={
                    'period_end': hour_end,
                    'total_requests': result['total'],
                    'successful_requests': result['successful'],
                    'failed_requests': result['failed'],
                    'avg_response_time': result['avg_time'] or 0,
                    'min_response_time': result['min_time'] or 0,
                    'max_response_time': result['max_time'] or 0,
                    'status_code_distribution': cls.get_status_code_distribution(
                        logs.filter(
                            project_id=result['project'],
                            api_definition_id=result['api_definition']
                        )
                    )
                }
            )
    
    @staticmethod
    def get_status_code_distribution(logs):
        """Get distribution of status codes."""
        distribution = {}
        for log in logs:
            status_code = str(log.status_code)
            distribution[status_code] = distribution.get(status_code, 0) + 1
        return distribution
        