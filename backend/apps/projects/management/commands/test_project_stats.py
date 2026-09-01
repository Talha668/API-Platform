from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.projects.models import Project
from apps.api_logs.models import RequestLog

User = get_user_model()


class Command(BaseCommand):
    help = 'Test project statistics properties'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project-id',
            type=int,
            help='Project ID to test'
        )
        parser.add_argument(
            '--create-sample',
            action='store_true',
            help='Create sample request logs for testing'
        )

    def handle(self, *args, **options):
        project_id = options.get('project_id')
        
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Project {project_id} not found'))
                return
        else:
            # Get first project
            project = Project.objects.first()
            if not project:
                self.stdout.write(self.style.ERROR('No projects found. Create a project first.'))
                return
        
        self.stdout.write(f'Testing statistics for project: {project.name} (ID: {project.id})')
        self.stdout.write('=' * 50)
        
        # Test all properties
        properties = [
            ('total_requests', project.total_requests),
            ('successful_requests', project.successful_requests),
            ('failed_requests', project.failed_requests),
            ('error_rate', project.error_rate),
            ('avg_response_time', project.avg_response_time),
            ('api_keys_count', project.api_keys_count),
            ('enabled_apis_count', project.enabled_apis_count),
            ('total_requests_today', project.total_requests_today),
            ('total_requests_this_week', project.total_requests_this_week),
            ('rate_limit', project.rate_limit),
            ('rate_limit_daily', project.rate_limit_daily),
            ('rate_limit_remaining', project.rate_limit_remaining),
        ]
        
        for name, value in properties:
            self.stdout.write(f'  {name}: {value}')
        
        self.stdout.write('=' * 50)
        
        # Test detailed usage stats
        self.stdout.write('\nDetailed usage stats (last 7 days):')
        usage = project.get_usage_stats()
        self.stdout.write(f'  Summary:')
        self.stdout.write(f'    Total: {usage["summary"]["total"]}')
        self.stdout.write(f'    Success: {usage["summary"]["successful"]}')
        self.stdout.write(f'    Failed: {usage["summary"]["failed"]}')
        self.stdout.write(f'    Error Rate: {usage["summary"]["error_rate"]}%')
        self.stdout.write(f'    Avg Response: {usage["summary"]["avg_response_time"]}ms')
        
        self.stdout.write('\n  Top Endpoints:')
        for endpoint in usage['top_endpoints'][:5]:
            self.stdout.write(f'    {endpoint["path"]}: {endpoint["total"]} requests')
        
        self.stdout.write('\n  Status Code Distribution:')
        for status, count in usage['status_distribution'].items():
            self.stdout.write(f'    {status}: {count} requests')
        
        self.stdout.write('=' * 50)
        
        # Test rate limit usage
        self.stdout.write('\nRate Limit Usage:')
        rate_usage = project.get_rate_limit_usage()
        self.stdout.write(f'  Tier: {rate_usage["tier"]}')
        self.stdout.write(f'  Hourly: {rate_usage["hourly"]["used"]}/{rate_usage["hourly"]["limit"]} (remaining: {rate_usage["hourly"]["remaining"]})')
        self.stdout.write(f'  Daily: {rate_usage["daily"]["used"]}/{rate_usage["daily"]["limit"]} (remaining: {rate_usage["daily"]["remaining"]})')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Project statistics test complete!'))