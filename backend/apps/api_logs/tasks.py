from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import RequestLog, AggregatedMetric



@shared_task
def aggregate_metrics():
    """
    Aggregate request logs into hourly metrics.
    Called by Celery Beat scheduler.
    """
    # Get the previous hour
    now = timezone.now()
    hour_start = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
    hour_end = hour_start + timedelta(hours=1)
    
    # Check if metrics already exist for this hour
    exists = AggregatedMetric.objects.filter(
        metric_type=AggregatedMetric.MetricType.HOURLY,
        period_start=hour_start
    ).exists()
    
    if not exists:
        AggregatedMetric.aggregate_hourly(hour_start)
        return f"Aggregated metrics for {hour_start}"
    else:
        return f"Metrics already exist for {hour_start}"


@shared_task
def aggregate_daily_metrics():
    """
    Aggregate daily metrics from hourly metrics.
    """
    now = timezone.now()
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    day_end = day_start + timedelta(days=1)
    
    # Aggregate from hourly metrics
    hourly_metrics = AggregatedMetric.objects.filter(
        metric_type=AggregatedMetric.MetricType.HOURLY,
        period_start__gte=day_start,
        period_start__lt=day_end
    )
    
    # Group by project and API definition
    from django.db.models import Sum, Avg, Max, Min
    results = hourly_metrics.values('project', 'api_definition').annotate(
        total_requests=Sum('total_requests'),
        successful_requests=Sum('successful_requests'),
        failed_requests=Sum('failed_requests'),
        avg_response_time=Avg('avg_response_time'),
        max_response_time=Max('max_response_time'),
        min_response_time=Min('min_response_time'),
    )
    
    for result in results:
        # Combine status code distributions
        status_distribution = {}
        for metric in hourly_metrics.filter(
            project_id=result['project'],
            api_definition_id=result['api_definition']
        ):
            for status, count in metric.status_code_distribution.items():
                status_distribution[status] = status_distribution.get(status, 0) + count
        
        AggregatedMetric.objects.update_or_create(
            project_id=result['project'],
            api_definition_id=result['api_definition'],
            metric_type=AggregatedMetric.MetricType.DAILY,
            period_start=day_start,
            defaults={
                'period_end': day_end,
                'total_requests': result['total_requests'],
                'successful_requests': result['successful_requests'],
                'failed_requests': result['failed_requests'],
                'avg_response_time': result['avg_response_time'] or 0,
                'min_response_time': result['min_response_time'] or 0,
                'max_response_time': result['max_response_time'] or 0,
                'status_code_distribution': status_distribution,
            }
        )
    
    return f"Aggregated daily metrics for {day_start}"