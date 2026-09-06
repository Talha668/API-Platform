from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from apps.projects.models import Project
from apps.api_keys.models import APIKey

class Command(BaseCommand):
    help = 'Seed database with dummy API keys'

    def handle(self, *args, **options):
        self.stdout.write('Seeding API keys...')
        
        projects = Project.objects.filter(is_active=True)
        
        if not projects.exists():
            self.stdout.write(self.style.ERROR('No projects found. Please run seed_projects first.'))
            return

        key_names = [
            'Production Key',
            'Development Key',
            'Staging Key',
            'Mobile App Key',
            'Web App Key',
            'Admin Console Key',
            'Integration Key',
            'External Partner Key',
            'Internal Service Key',
            'Microservice Key',
            'Frontend App Key',
            'Backend Service Key',
        ]

        scopes = ['read', 'write', 'admin']
        created_count = 0

        for project in projects:
            # Create 2-5 keys per project
            num_keys = random.randint(2, 5)
            
            for i in range(num_keys):
                name = random.choice(key_names) + f' {i+1}'
                scope = random.choice(scopes)
                is_active = random.random() > 0.2  # 80% active
                has_expiry = random.random() > 0.3  # 70% have expiry
                
                # Generate the key
                full_key, prefix, key_hash = APIKey.generate_key()
                
                # Create the key
                key = APIKey(
                    project=project,
                    name=name,
                    key_prefix=prefix,
                    key_hash=key_hash,
                    scope=scope,
                    is_active=is_active,
                    created_at=timezone.now() - timedelta(days=random.randint(1, 90)),
                    last_used_at=timezone.now() - timedelta(hours=random.randint(1, 720)) if is_active and random.random() > 0.3 else None,
                )
                
                if has_expiry:
                    key.expires_at = timezone.now() + timedelta(days=random.randint(30, 365))
                
                key.save()
                created_count += 1
                self.stdout.write(f'  Created key: {key.name} for project {project.name}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} API keys!')
        )