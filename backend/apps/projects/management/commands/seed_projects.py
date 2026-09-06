from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random
from apps.projects.models import Project

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed database with dummy projects'

    def handle(self, *args, **options):
        self.stdout.write('Seeding projects...')
        
        # Get all users
        users = User.objects.all()
        
        if not users.exists():
            self.stdout.write(self.style.ERROR('No users found. Please run seed_users first.'))
            return

        projects_data = [
            {
                'name': 'Weather API Service',
                'description': 'Enterprise weather data service with real-time updates and historical data access',
                'tier': 'enterprise',
                'custom_rate_limit': 50000,
            },
            {
                'name': 'Task Management Platform',
                'description': 'Complete task management solution with team collaboration features',
                'tier': 'pro',
                'custom_rate_limit': 15000,
            },
            {
                'name': 'Currency Exchange Service',
                'description': 'Real-time currency conversion and historical exchange rate API',
                'tier': 'pro',
                'custom_rate_limit': 10000,
            },
            {
                'name': 'Social Media Analytics',
                'description': 'Track and analyze social media engagement metrics',
                'tier': 'enterprise',
                'custom_rate_limit': 75000,
            },
            {
                'name': 'E-commerce Product API',
                'description': 'Product catalog, inventory management, and pricing API',
                'tier': 'pro',
                'custom_rate_limit': 20000,
            },
            {
                'name': 'Healthcare Data API',
                'description': 'HIPAA-compliant healthcare data management API',
                'tier': 'enterprise',
                'custom_rate_limit': 100000,
            },
            {
                'name': 'Financial Market Data',
                'description': 'Real-time stock market data and analysis API',
                'tier': 'enterprise',
                'custom_rate_limit': 50000,
            },
            {
                'name': 'Geolocation Service',
                'description': 'IP-based geolocation and mapping API',
                'tier': 'pro',
                'custom_rate_limit': 12000,
            },
            {
                'name': 'Email Marketing Platform',
                'description': 'Transactional and marketing email delivery API',
                'tier': 'pro',
                'custom_rate_limit': 18000,
            },
            {
                'name': 'Image Processing Service',
                'description': 'AI-powered image recognition and processing API',
                'tier': 'enterprise',
                'custom_rate_limit': 30000,
            },
            {
                'name': 'Payment Gateway Integration',
                'description': 'Multi-provider payment processing API',
                'tier': 'enterprise',
                'custom_rate_limit': 40000,
            },
            {
                'name': 'Notification Delivery Service',
                'description': 'Push notifications, SMS, and email delivery API',
                'tier': 'pro',
                'custom_rate_limit': 25000,
            },
        ]

        created_count = 0
        for project_data in projects_data:
            # Assign random owner
            owner = random.choice(users)
            
            # Create project with random dates
            created_at = timezone.now() - timedelta(days=random.randint(1, 180))
            
            project = Project.objects.create(
                owner=owner,
                name=project_data['name'],
                description=project_data['description'],
                tier=project_data['tier'],
                custom_rate_limit=project_data['custom_rate_limit'],
                is_active=True,
                created_at=created_at,
                updated_at=created_at + timedelta(days=random.randint(1, 30))
            )
            
            created_count += 1
            self.stdout.write(f'  Created project: {project.name} (Owner: {owner.email})')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} projects!')
        )