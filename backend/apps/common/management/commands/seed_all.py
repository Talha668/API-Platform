from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Seed all dummy data for development'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting complete database seeding...'))
        self.stdout.write('=' * 50)
        
        # Seed in order of dependencies
        commands = [
            ('seed_users', 'Creating users...'),
            ('seed_projects', 'Creating projects...'),
            ('seed_api_keys', 'Creating API keys...'),
            ('seed_apis', 'Creating API definitions...'),  # This is from gateway
            ('seed_gateway_data', 'Creating additional gateway data...'),
            ('seed_logs', 'Creating request logs...'),
        ]
        
        for command, description in commands:
            self.stdout.write(f'\n{description}')
            try:
                call_command(command)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error running {command}: {str(e)}'))
                continue
        
        self.stdout.write('=' * 50)
        self.stdout.write(self.style.SUCCESS('✅ Complete database seeding finished!'))
        self.stdout.write('\nSample API Keys (for testing):')
        self.stdout.write('  - Email: john.doe@example.com')
        self.stdout.write('  - Password: SecurePass123!')
        self.stdout.write('\n  - Email: jane.smith@example.com')
        self.stdout.write('  - Password: SecurePass123!')
        self.stdout.write('\n  - Email: bob.wilson@example.com')
        self.stdout.write('  - Password: SecurePass123!')