import redis
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Check Redis connection and rate limit keys'

    def handle(self, *args, **options):
        self.stdout.write('Checking Redis status...')
        
        try:
            # Connect to Redis
            r = redis.from_url(settings.REDIS_URL, decode_responses=True)
            
            # Get Redis info
            info = r.info()
            
            self.stdout.write(self.style.SUCCESS('Redis connection successful!'))
            self.stdout.write(f'Redis version: {info.get("redis_version")}')
            self.stdout.write(f'Connected clients: {info.get("connected_clients")}')
            self.stdout.write(f'Used memory: {info.get("used_memory_human")}')
            self.stdout.write(f'Total commands processed: {info.get("total_commands_processed")}')
            
            # Get rate limit keys
            self.stdout.write('\nRate limit keys:')
            keys = r.keys('rate_limit:*')
            
            if keys:
                for key in keys[:10]:  # Show first 10
                    ttl = r.ttl(key)
                    count = r.zcard(key)
                    self.stdout.write(f'  {key} - Count: {count}, TTL: {ttl}s')
                
                if len(keys) > 10:
                    self.stdout.write(f'  ... and {len(keys) - 10} more keys')
            else:
                self.stdout.write('  No rate limit keys found.')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Redis error: {str(e)}'))