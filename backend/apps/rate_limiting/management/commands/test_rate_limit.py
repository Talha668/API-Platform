import time
import requests
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Test rate limiting functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--requests',
            type=int,
            default=10,
            help='Number of requests to make'
        )
        parser.add_argument(
            '--url',
            type=str,
            default='http://localhost:8000/external/v1/weather',
            help='URL to test'
        )
        parser.add_argument(
            '--api-key',
            type=str,
            help='API key to use for authentication'
        )

    def handle(self, *args, **options):
        self.stdout.write('Testing rate limiting...')
        
        url = options['url']
        num_requests = options['requests']
        api_key = options.get('api_key')
        
        if not api_key:
            self.stdout.write(self.style.ERROR('API key is required. Please provide --api-key'))
            return
        
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        
        self.stdout.write(f'Sending {num_requests} requests to {url}')
        self.stdout.write('-' * 50)
        
        for i in range(num_requests):
            response = requests.get(url, headers=headers)
            
            # Print response details
            status_color = self.style.SUCCESS if response.status_code == 200 else self.style.ERROR
            self.stdout.write(
                status_color(
                    f'Request {i+1}: Status {response.status_code}'
                )
            )
            
            # Print rate limit headers
            if 'X-RateLimit-Limit' in response.headers:
                self.stdout.write(
                    f'  Limit: {response.headers.get("X-RateLimit-Limit")}'
                )
                self.stdout.write(
                    f'  Remaining: {response.headers.get("X-RateLimit-Remaining")}'
                )
                self.stdout.write(
                    f'  Reset: {response.headers.get("X-RateLimit-Reset")}'
                )
            
            # If rate limited, show response
            if response.status_code == 429:
                self.stdout.write(
                    self.style.WARNING(f'  Response: {response.json()}')
                )
            
            self.stdout.write('')
            
            # Small delay between requests
            if i < num_requests - 1:
                time.sleep(0.1)
        
        self.stdout.write(self.style.SUCCESS('Rate limiting test complete!'))