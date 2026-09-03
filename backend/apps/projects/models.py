from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg, Sum, Count
from apps.common.choices import SubscriptionTier




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

    # Rate limiting
    custom_rate_limit = models.IntegerField(_('custom rate limit per hour'), blank=True, null=True, help_text='Override default rate limit for this project')
    tier = models.CharField(_('tier'), max_length=20, choices=SubscriptionTier.choices, default=SubscriptionTier.FREE, db_index=True)
    
    class Meta:
        db_table = 'projects'
        verbose_name = _('project')
        verbose_name_plural = _('projects')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'created_at']),
            models.Index(fields=['is_active']),
            models.Index(fields=['tier']),
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
        try:
            from apps.api_logs.models import RequestLog
            return RequestLog.objects.filter(project=self).count()
        except (ImportError, AttributeError):
            return 0

    @property
    def successful_requests(self):
        """
        Get total number of successfull requests (status < 400) for this project.
        """
        try:
            from apps.api_logs.models import RequestLog
            return RequestLog.objects.filter(
                project=self,
                status_code__lt=400,
            ).count()
        except (ImportError, AttributeError):
            return 0

    @property
    def failed_requests(self):
        """
        Get the total number of failed requsts (status < 400) for this project.
        """
        try:
            from apps.api_logs.models import RequestLog
            return RequestLog.objects.filter(
                project=self,
                status_code__lt=400,
            ).count()
        except (ImportError, AttributeError):
            return 0

    @property
    def error_rate(self):
        """
        Get the error rate as a percentage.
        """
        total = self.total_requests
        if total == 0:
            return 0.0
        return (self.failed_requests / total) * 100

    @property
    def avg_respomse_time(self):
        """
        Get the average response time in miliseconds.
        """
        try:
            from apps.api_logs.models import RequestLog
            result = RequestLog.objects.filter(project=self).aggregate(
                avg_time=Avg('response_time')
            )
            return result['avg_time'] or 0.0
        except (ImportError, AttributeError):
            return 0.0
         
    @property
    def api_keys_count(self):
        """Get the number of active API keys for this project."""
        return self.api_keys.filter(is_active=True).count()

    @property
    def enabled_apis_count(self):
        """
        Get the number of enabled APIs for this project.
        """
        try:
            from apps.gateway.models import ProjectAPIAssignment
            return ProjectAPIAssignment.objects.filter(
                project=self,
                is_enabled=True
            ).count()
        except (ImportError, AttributeError):
            return 0
    
    @property
    def total_requests_today(self):
        """
        Get the total number of requests for today.
        """
        try:
            from apps.api_logs.models import RequestLog
            today = timezone.now().date()
            return RequestLog.objects.filter(
                project=self,
                created_at__date=today
            ).count()
        except (ImportError, AttributeError):
            return 0
    
    @property
    def total_requests_this_week(self):
        """
        Get the total number of requests for this week.
        """
        try:
            from apps.api_logs.models import RequestLog
            today = timezone.now().date()
            start_of_week = today - timezone.timedelta(days=today.weekday())
            return RequestLog.objects.filter(
                project=self,
                created_at__date__gte=start_of_week
            ).count()
        except (ImportError, AttributeError):
            return 0
    
    def get_usage_stats(self, days=7):
        """
        Get usage statistics for the project over the last N days.
        """
        try:
            from apps.api_logs.models import RequestLog
            from datetime import timedelta
            
            start_date = timezone.now() - timedelta(days=days)
            
            # Get daily request counts
            daily_stats = (
                RequestLog.objects
                .filter(project=self, created_at__gte=start_date)
                .extra({'day': "date(created_at)"})
                .values('day')
                .annotate(
                    total=Count('id'),
                    successful=Count('id', filter=models.Q(status_code__lt=400)),
                    failed=Count('id', filter=models.Q(status_code__gte=400)),
                    avg_response=Avg('response_time')
                )
                .order_by('day')
            )
            
            # Get endpoint statistics
            endpoint_stats = (
                RequestLog.objects
                .filter(project=self, created_at__gte=start_date)
                .values('path')
                .annotate(
                    total=Count('id'),
                    avg_response=Avg('response_time')
                )
                .order_by('-total')[:10]
            )
            
            # Get status code distribution
            status_distribution = (
                RequestLog.objects
                .filter(project=self, created_at__gte=start_date)
                .values('status_code')
                .annotate(count=Count('id'))
                .order_by('-count')
            )
            
            return {
                'daily_stats': list(daily_stats),
                'top_endpoints': list(endpoint_stats),
                'status_distribution': {
                    str(item['status_code']): item['count']
                    for item in status_distribution
                },
                'summary': {
                    'total': self.total_requests,
                    'successful': self.successful_requests,
                    'failed': self.failed_requests,
                    'error_rate': round(self.error_rate, 2),
                    'avg_response_time': round(self.avg_response_time, 2),
                }
            }
        except (ImportError, AttributeError):
            return {
                'daily_stats': [],
                'top_endpoints': [],
                'status_distribution': {},
                'summary': {
                    'total': 0,
                    'successful': 0,
                    'failed': 0,
                    'error_rate': 0,
                    'avg_response_time': 0,
                }
            }
    
    @property
    def rate_limit(self):
        """
        Get the effective rate limit for this project.
        """
        # Check if project has custom rate limit
        if self.custom_rate_limit:
            return self.custom_rate_limit
        
        # Check tier-based limits
        from apps.rate_limiting.services import TieredRateLimiter
        tier_limits = TieredRateLimiter.TIERS.get(self.tier, TieredRateLimiter.TIERS['free'])
        return tier_limits.get('requests_per_hour', 100)
    
    @property
    def rate_limit_daily(self):
        """
        Get the daily rate limit for this project.
        """
        from apps.rate_limiting.services import TieredRateLimiter
        tier_limits = TieredRateLimiter.TIERS.get(self.tier, TieredRateLimiter.TIERS['free'])
        return tier_limits.get('requests_per_day', 1000)
    
    @property
    def rate_limit_remaining(self):
        """
        Get the remaining rate limit for this project.
        """
        try:
            from apps.rate_limiting.services import RateLimiter
            rate_limiter = RateLimiter()
            usage = rate_limiter.get_usage(f"project_{self.id}")
            return usage.get('remaining', 0)
        except (ImportError, AttributeError):
            return 0
    
    def get_rate_limit_usage(self):
        """
        Get detailed rate limit usage for this project.
        """
        try:
            from apps.rate_limiting.services import TieredRateLimiter
            rate_limiter = TieredRateLimiter()
            return rate_limiter.get_usage(f"project_{self.id}", self.tier)
        except (ImportError, AttributeError):
            return {
                'tier': self.tier,
                'hourly': {'used': 0, 'limit': 100, 'remaining': 100},
                'daily': {'used': 0, 'limit': 1000, 'remaining': 1000},
            }