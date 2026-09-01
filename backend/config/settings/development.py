from .base import *

DEBUG = True

# Use console email backend in development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable secure cookie requirements in development
JWT_COOKIE_SECURE = False

# Add debug toolbar
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    
    # Debug toolbar configuration
    INTERNAL_IPS = [
        '127.0.0.1',
    ]

# Database - for development, you might want SQLite for quick setup
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }