from django.db.models import Count, Avg, Sum, Q, F
from django.utils import timezone
from datetime import timedelta
from .models import RequestLog, AggregatedMetric


class AnalyticsService:
    """
    Service for generating analytics from request logs.
    """
    
    @staticmethod
    def get_project_analytics(project_id, days=7):
        """
        Get analytics for a specific project over a time period.
        """
        start_date = timezone.now() - timedelta(days=days)
        
        logs = RequestLog.objects.filter(
            project_id=project_id,
            created_at__gte=start_date
        )
        
        # Basic metrics
        total_requests = logs.count()
        successful_requests = logs.filter(status_code__lt=400).count()
        failed_requests = logs.filter(status_code__gte=400).count()
        error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Response time metrics
        avg_response_time = logs.aggregate(Avg('response_time'))['response_time__avg'] or 0
        min_response_time = logs.aggregate(Min('response_time'))['response_time__min'] or 0
        max_response_time = logs.aggregate(Max('response_time'))['response_time__max'] or 0
        
        # Status code distribution
        status_distribution = {}
        for log in logs.values('status_code').annotate(count=Count('id')):
            status_distribution[str(log['status_code'])] = log['count']
        
        # Requests by endpoint
        endpoint_requests = []
        for result in logs.values('path').annotate(count=Count('id')).order_by('-count')[:10]:
            endpoint_requests.append({
                'endpoint': result['path'],
                'count': result['count']
            })
        
        # Requests over time (daily)
        daily_requests = []
        for i in range(days):
            day = start_date + timedelta(days=i)
            next_day = day + timedelta(days=1)
            day_count = logs.filter(
                created_at__gte=day,
                created_at__lt=next_day
            ).count()
            daily_requests.append({
                'date': day.date().isoformat(),
                'count': day_count
            })
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'error_rate': round(error_rate, 2),
            'avg_response_time': round(avg_response_time, 2),
            'min_response_time': min_response_time,
            'max_response_time': max_response_time,
            'status_distribution': status_distribution,
            'top_endpoints': endpoint_requests,
            'daily_requests': daily_requests,
        }
    
    @staticmethod
    def get_api_analytics(project_id, api_definition_id, days=7):
        """
        Get analytics for a specific API within a project.
        """
        start_date = timezone.now() - timedelta(days=days)
        
        logs = RequestLog.objects.filter(
            project_id=project_id,
            api_definition_id=api_definition_id,
            created_at__gte=start_date
        )
        
        total_requests = logs.count()
        successful_requests = logs.filter(status_code__lt=400).count()
        failed_requests = logs.filter(status_code__gte=400).count()
        error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
        
        avg_response_time = logs.aggregate(Avg('response_time'))['response_time__avg'] or 0
        
        # Requests over time (hourly)
        hourly_requests = []
        for i in range(days * 24):
            hour = start_date + timedelta(hours=i)
            next_hour = hour + timedelta(hours=1)
            hour_count = logs.filter(
                created_at__gte=hour,
                created_at__lt=next_hour
            ).count()
            if hour_count > 0 or i % 24 == 0:  # Show all hours with data, plus midnight
                hourly_requests.append({
                    'hour': hour.isoformat(),
                    'count': hour_count
                })
        
        return {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'error_rate': round(error_rate, 2),
            'avg_response_time': round(avg_response_time, 2),
            'hourly_requests': hourly_requests,
        }