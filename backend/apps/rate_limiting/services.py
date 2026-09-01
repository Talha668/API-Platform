import time
import redis
from django.conf import settings
from django.core.cache import cache
from typing import Tuple, Optional





class RateLimiter:
    """
    Redis-based rate limiter using sliding window algorithm.
    """
    
    def __init__(self, key_prefix='rate_limit'):
        self.key_prefix = key_prefix
        self.redis_client = self._get_redis_client()
    
    def _get_redis_client(self):
        """Get Redis client connection."""
        try:
            return redis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception as e:
            # Fallback to Django cache if Redis is not available
            return None
    
    def get_rate_limit_key(self, identifier: str, resource: str = 'default') -> str:
        """
        Generate a unique Redis key for rate limiting.
        """
        return f"{self.key_prefix}:{resource}:{identifier}"
    
    def is_rate_limited(
        self, 
        identifier: str, 
        limit: int, 
        window: int,
        resource: str = 'default'
    ) -> Tuple[bool, dict]:
        """
        Check if the request should be rate limited.
        Returns (is_limited, response_data)
        """
        # Skip rate limiting if Redis is not available
        if not self.redis_client:
            return False, {'limit': limit, 'remaining': limit, 'reset': int(time.time()) + window}
        
        key = self.get_rate_limit_key(identifier, resource)
        current_time = int(time.time())
        window_start = current_time - window
        
        # Use Redis pipeline for atomic operations
        pipe = self.redis_client.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Add current request
        pipe.zadd(key, {str(current_time): current_time})
        
        # Set expiry on the key
        pipe.expire(key, window)
        
        # Count requests in the current window
        pipe.zcard(key)
        
        # Execute pipeline
        results = pipe.execute()
        
        # Get the count (last result from pipeline)
        request_count = results[-1]
        
        # Calculate remaining and reset time
        remaining = max(0, limit - request_count)
        reset_time = window_start + window
        
        response_data = {
            'limit': limit,
            'remaining': remaining,
            'reset': reset_time,
            'retry_after': reset_time - current_time if request_count >= limit else 0
        }
        
        # Check if rate limited
        is_limited = request_count > limit
        
        return is_limited, response_data
    
    def get_usage(self, identifier: str, resource: str = 'default') -> dict:
        """
        Get current usage statistics for a given identifier.
        """
        if not self.redis_client:
            return {'count': 0, 'remaining': 0, 'reset': 0}
        
        key = self.get_rate_limit_key(identifier, resource)
        current_time = int(time.time())
        
        # Get all timestamps in the current window
        timestamps = self.redis_client.zrangebyscore(key, current_time - 3600, current_time)
        
        return {
            'count': len(timestamps),
            'remaining': max(0, 100 - len(timestamps)),  # Default limit
            'reset': current_time + 3600
        }
    
    def reset_usage(self, identifier: str, resource: str = 'default'):
        """
        Reset rate limit usage for a given identifier.
        """
        if not self.redis_client:
            return
        
        key = self.get_rate_limit_key(identifier, resource)
        self.redis_client.delete(key)
    
    def get_project_limit(self, project, api_definition=None) -> Tuple[int, int]:
        """
        Get rate limit for a project and optional API.
        Returns (limit, window_in_seconds)
        """
        # Default limits
        default_limit = settings.RATE_LIMIT.get('DEFAULT_LIMIT', 100)
        default_window = settings.RATE_LIMIT.get('DEFAULT_WINDOW', 3600)
        
        # Check if project has custom limit
        if hasattr(project, 'rate_limit') and project.rate_limit:
            return project.rate_limit, default_window
        
        # Check if API has custom limit
        if api_definition and api_definition.default_rate_limit:
            return api_definition.default_rate_limit, default_window
        
        return default_limit, default_window


class TieredRateLimiter:
    """
    Rate limiter with tier-based limits (Free, Pro, Enterprise).
    """
    
    TIERS = {
        'free': {
            'requests_per_hour': 100,
            'requests_per_day': 1000,
            'concurrent_requests': 5,
        },
        'pro': {
            'requests_per_hour': 10000,
            'requests_per_day': 100000,
            'concurrent_requests': 50,
        },
        'enterprise': {
            'requests_per_hour': 100000,
            'requests_per_day': 1000000,
            'concurrent_requests': 500,
        },
    }
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
    
    def get_tier_limits(self, tier: str = 'free') -> dict:
        """
        Get rate limits for a specific tier.
        """
        return self.TIERS.get(tier.lower(), self.TIERS['free'])
    
    def check_rate_limit(
        self, 
        identifier: str, 
        tier: str = 'free',
        api_definition=None
    ) -> Tuple[bool, dict]:
        """
        Check rate limit based on tier.
        Returns (is_limited, response_data)
        """
        limits = self.get_tier_limits(tier)
        
        # Check hourly limit
        is_limited_hourly, hourly_data = self.rate_limiter.is_rate_limited(
            identifier=identifier,
            limit=limits['requests_per_hour'],
            window=3600,  # 1 hour
            resource=f"{api_definition.slug if api_definition else 'default'}:hourly"
        )
        
        if is_limited_hourly:
            return True, {
                'error': 'RateLimitExceeded',
                'detail': f'Hourly rate limit of {limits["requests_per_hour"]} requests exceeded.',
                'limit': hourly_data['limit'],
                'remaining': 0,
                'reset': hourly_data['reset'],
                'retry_after': hourly_data['retry_after']
            }
        
        # Check daily limit
        is_limited_daily, daily_data = self.rate_limiter.is_rate_limited(
            identifier=identifier,
            limit=limits['requests_per_day'],
            window=86400,  # 24 hours
            resource=f"{api_definition.slug if api_definition else 'default'}:daily"
        )
        
        if is_limited_daily:
            return True, {
                'error': 'RateLimitExceeded',
                'detail': f'Daily rate limit of {limits["requests_per_day"]} requests exceeded.',
                'limit': daily_data['limit'],
                'remaining': 0,
                'reset': daily_data['reset'],
                'retry_after': daily_data['retry_after']
            }
        
        # Return success with usage data
        return False, {
            'limit': limits['requests_per_hour'],
            'remaining': hourly_data['remaining'],
            'reset': hourly_data['reset'],
            'tier': tier
        }
    
    def get_usage(self, identifier: str, tier: str = 'free') -> dict:
        """
        Get current usage statistics.
        """
        limits = self.get_tier_limits(tier)
        
        hourly_usage = self.rate_limiter.get_usage(identifier, 'default:hourly')
        daily_usage = self.rate_limiter.get_usage(identifier, 'default:daily')
        
        return {
            'tier': tier,
            'hourly': {
                'used': hourly_usage['count'],
                'limit': limits['requests_per_hour'],
                'remaining': max(0, limits['requests_per_hour'] - hourly_usage['count']),
            },
            'daily': {
                'used': daily_usage['count'],
                'limit': limits['requests_per_day'],
                'remaining': max(0, limits['requests_per_day'] - daily_usage['count']),
            },
        }