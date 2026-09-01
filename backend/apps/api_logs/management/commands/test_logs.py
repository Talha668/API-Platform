from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.api_logs.models import RequestLog


class Command(BaseCommand):
    help = 'Test request logging by creating sample logs'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample request logs...')
        
        # Get a project
        from apps.projects.models import Project
        project = Project.objects.first()
        
        if not project:
            self.stdout.write(self.style.ERROR('No project found. Create a project first.'))
            return
        
        # Create sample logs
        status_codes = [200, 200, 200, 200, 201, 404, 500, 429]
        endpoints = ['/v1/weather', '/v1/tasks', '/v1/currency', '/v1/weather/forecast']
        
        for i in range(50):
            RequestLog.objects.create(
                project=project,
                api_key=None,
                method='GET' if i % 3 != 0 else 'POST',
                path=endpoints[i % len(endpoints)],
                status_code=status_codes[i % len(status_codes)],
                response_time=50 + (i * 10) % 200,
                ip_address='127.0.0.1',
                user_agent='Test Agent/1.0',
                is_error=status_codes[i % len(status_codes)] >= 400,
                created_at=timezone.now() - timezone.timedelta(hours=i)
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Created 50 sample request logs for project "{project.name}"')
        )