from django.db import models
from django.utils.translation import gettext_lazy as _




class SubscriptionTier(models.TextChoices):
    """Subscription tier"""
    FREE = 'free', 'Free'
    PRO = 'pro', 'Pro'
    ENTERPRISE = 'enterprise', 'Enterprise'