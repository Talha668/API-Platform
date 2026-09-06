from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed database with dummy users'

    def handle(self, *args, **options):
        self.stdout.write('Seeding users...')
        
        # Create users with different tiers
        users_data = [
            {
                'email': 'john.doe@example.com',
                'password': 'SecurePass123!',
                'first_name': 'John',
                'last_name': 'Doe',
                'company': 'TechCorp Inc.',
                'bio': 'Full-stack developer with 10 years of experience',
                'subscription_tier': 'enterprise',
                'subscription_ends_at': timezone.now() + timedelta(days=365),
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'email': 'jane.smith@example.com',
                'password': 'SecurePass123!',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'company': 'DevStudio LLC',
                'bio': 'API architect and cloud specialist',
                'subscription_tier': 'pro',
                'subscription_ends_at': timezone.now() + timedelta(days=180),
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'email': 'bob.wilson@example.com',
                'password': 'SecurePass123!',
                'first_name': 'Bob',
                'last_name': 'Wilson',
                'company': 'StartupHub',
                'bio': 'Building the next generation of API tools',
                'subscription_tier': 'free',
                'subscription_ends_at': None,
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'email': 'alice.johnson@example.com',
                'password': 'SecurePass123!',
                'first_name': 'Alice',
                'last_name': 'Johnson',
                'company': 'Enterprise Solutions',
                'bio': 'DevOps engineer passionate about automation',
                'subscription_tier': 'enterprise',
                'subscription_ends_at': timezone.now() + timedelta(days=730),
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'email': 'charlie.brown@example.com',
                'password': 'SecurePass123!',
                'first_name': 'Charlie',
                'last_name': 'Brown',
                'company': 'Freelance Dev',
                'bio': 'Independent developer building API-first applications',
                'subscription_tier': 'pro',
                'subscription_ends_at': timezone.now() + timedelta(days=90),
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'email': 'diana.prince@example.com',
                'password': 'SecurePass123!',
                'first_name': 'Diana',
                'last_name': 'Prince',
                'company': 'TechInnovate',
                'bio': 'CTO with focus on scalable architectures',
                'subscription_tier': 'enterprise',
                'subscription_ends_at': timezone.now() + timedelta(days=365),
                'is_staff': True,
                'is_superuser': False,
            },
        ]

        created_count = 0
        for user_data in users_data:
            email = user_data.pop('email')
            password = user_data.pop('password')
            
            # Check if user already exists
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    **user_data
                )
                created_count += 1
                self.stdout.write(f'  Created user: {email}')
            else:
                self.stdout.write(f'  User already exists: {email}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} users!')
        )