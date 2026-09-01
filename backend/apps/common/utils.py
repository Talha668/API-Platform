import hashlib
import secrets
from django.utils import timezone


def generate_secure_token(length=32):
    """
    Generate a cryptographically secure random token.
    """
    return secrets.token_urlsafe(length)


def hash_string(value):
    """
    Hash a string using SHA-256.
    """
    return hashlib.sha256(value.encode()).hexdigest()


def generate_short_uuid():
    """
    Generate a short unique identifier.
    """
    import uuid
    return str(uuid.uuid4())[:8]


def format_datetime(dt):
    """
    Format a datetime object to ISO format.
    """
    if dt:
        return dt.isoformat()
    return None


def parse_datetime(dt_str):
    """
    Parse a datetime string from ISO format.
    """
    from datetime import datetime
    try:
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return None