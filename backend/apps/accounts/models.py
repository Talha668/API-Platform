from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """
    Custom User model that uses email as the username field
    """
    username = None    # Remove the username field

    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _('A user with that email already exists.'),
        },
    )

    # Additional fields
    company = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    # Track user activity
    last_active_at = models.DateTimeField(default=timezone.now)

    # Subscription tier
    class Tier(models.TextChoices):
        FREE = 'free', 'Free'
        PRO = 'pro', 'PRO'
        ENTERPRISE = 'enterprose', 'ENTERPRISE'

    subscription_tier = models.CharField(_('subscription tier'), max_length=20, choices=Tier.choices, default=Tier.FREE, db_index=True)
    subscription_ends_at = models.DateTimeField(_('subscription ends at'), blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []    # Email and password are required by  default

    objects = UserManager()

    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.email

    def get_full_name(self):
        """
        Return the full name of the user.
        """   
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email

    def get_short_name(self):
        """
        Return the short name of the user.
        """
        return self.first_name or self.email

    @property
    def is_verified(self):
        """
        Check if the user has verified their email.
        Implement email verification later.
        """
        return True    # For now all users will be appeared verified

    def update_last_active(self):
        """Update the last active timestamp"""
        self.last_active_at = timezone.now()
        self.save(update_fields=['last_active_at'])