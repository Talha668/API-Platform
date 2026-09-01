import hashlib
import secrets
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class APIKey(models.Model):
    """
    Model representing an API key for accessing the API platform.
    """
    class Scope(models.TextChoices):
        READ = 'read', _('Read Only')
        WRITE = 'write', _('Read and Write')
        ADMIN = 'admin', _('Full Access')
    
    # Relationship to project
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='api_keys',
        verbose_name=_('project')
    )
    
    # Key details
    name = models.CharField(_('key name'), max_length=255)
    key_prefix = models.CharField(_('key prefix'), max_length=10)
    key_hash = models.CharField(_('key hash'), max_length=128, db_index=True)
    scope = models.CharField(
        _('scope'),
        max_length=10,
        choices=Scope.choices,
        default=Scope.READ
    )
    
    # Status and tracking
    is_active = models.BooleanField(_('active'), default=True)
    last_used_at = models.DateTimeField(_('last used at'), blank=True, null=True)
    expires_at = models.DateTimeField(_('expires at'), blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    revoked_at = models.DateTimeField(_('revoked at'), blank=True, null=True)
    
    class Meta:
        db_table = 'api_keys'
        verbose_name = _('API key')
        verbose_name_plural = _('API keys')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'key_hash']),
            models.Index(fields=['is_active', 'expires_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.project.name})"
    
    @classmethod
    def generate_key(cls):
        """
        Generate a secure API key with a prefix.
        Returns a tuple (full_key, prefix, hash)
        """
        # Generate a cryptographically secure random string
        random_bytes = secrets.token_bytes(32)
        random_str = secrets.token_urlsafe(32)
        
        # Use the first 8 characters as prefix for display
        prefix = random_str[:8]
        
        # Create the full key with prefix
        full_key = f"sk_live_{prefix}_{random_str[8:]}"
        
        # Create hash for storage
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()
        
        return full_key, prefix, key_hash
    
    def update_last_used(self):
        """Update the last used timestamp."""
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])
    
    def revoke(self):
        """Revoke the API key."""
        self.is_active = False
        self.revoked_at = timezone.now()
        self.save(update_fields=['is_active', 'revoked_at'])
    
    def regenerate(self):
        """
        Regenerate the API key with a new secret.
        Returns the new full key (only shown once).
        """
        # Generate new key
        full_key, prefix, key_hash = self.generate_key()
        
        # Update the key
        self.key_prefix = prefix
        self.key_hash = key_hash
        self.save(update_fields=['key_prefix', 'key_hash'])
        
        return full_key
    
    @property
    def is_expired(self):
        """Check if the key has expired."""
        if self.expires_at:
            return timezone.now() >= self.expires_at
        return False
    
    @property
    def display_prefix(self):
        """Get the display prefix for the API key."""
        if len(self.key_prefix) >= 4:
            return f"sk_live_{self.key_prefix[:4]}...{self.key_prefix[-4:]}"
        return f"sk_live_{self.key_prefix}"