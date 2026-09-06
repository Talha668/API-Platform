from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
import json
from apps.projects.models import Project
from apps.api_keys.models import APIKey
from apps.gateway.models import APIDefinition
from apps.api_logs.models import RequestLog

class Command(BaseCommand):
    help = 'Seed database with dummy request logs'

    def handle(self, *args, **options):
        self.stdout.write('Seeding request logs...')
        
        projects = Project.objects.filter(is_active=True)
        api_keys = APIKey.objects.filter(is_active=True)
        api_definitions = APIDefinition.objects.filter(is_active=True)
        
        if not projects.exists():
            self.stdout.write(self.style.ERROR('No projects found. Please seed projects first.'))
            return

        # Generate logs for the last 30 days
        days_back = 30
        logs_per_day = random.randint(50, 200)
        total_logs = 0

        for day in range(days_back):
            day_date = timezone.now() - timedelta(days=day)
            num_logs = random.randint(20, logs_per_day)
            
            for _ in range(num_logs):
                project = random.choice(projects)
                api_key = random.choice(api_keys.filter(project=project)) if api_keys.filter(project=project).exists() else None
                api_def = random.choice(api_definitions) if random.random() > 0.3 else None
                
                # Random status codes with realistic distribution
                status_codes = [200, 200, 200, 200, 201, 200, 200, 400, 404, 429, 500]
                status_code = random.choice(status_codes)
                
                # Generate realistic response times
                if status_code < 400:
                    response_time = random.randint(10, 500)
                else:
                    response_time = random.randint(100, 2000)
                
                # Random methods
                methods = ['GET', 'GET', 'GET', 'POST', 'PUT', 'DELETE']
                method = random.choice(methods)
                
                # Random paths based on API definition
                if api_def:
                    path = api_def.path
                    # Replace {id} with random number if present
                    if '{id}' in path:
                        path = path.replace('{id}', str(random.randint(1, 100)))
                else:
                    path = random.choice(['/v1/weather', '/v1/tasks', '/v1/currencies', '/v1/users'])
                
                # Random IP addresses
                ip_parts = [str(random.randint(1, 255)) for _ in range(4)]
                ip_address = '.'.join(ip_parts)
                
                # Random user agents
                user_agents = [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
                    'PostmanRuntime/7.26.8',
                    'curl/7.68.0',
                    'python-requests/2.28.1',
                    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
                ]
                user_agent = random.choice(user_agents)
                
                # Create log entry
                log = RequestLog(
                    project=project,
                    api_key=api_key,
                    api_definition=api_def,
                    method=method,
                    path=path,
                    full_url=f'http://api.example.com{path}?param={random.randint(1, 100)}' if random.random() > 0.5 else f'http://api.example.com{path}',
                    status_code=status_code,
                    response_time=response_time,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    is_error=status_code >= 400,
                    is_authenticated=api_key is not None,
                    error_message=f'Error occurred: {status_code}' if status_code >= 400 else None,
                    created_at=day_date - timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59)),
                    processed_at=day_date - timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
                )
                log.save()
                total_logs += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {total_logs} request logs!')
        )