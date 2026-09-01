from django.apps import AppConfig


class ApiLogsConfig(AppConfig):
    default_auto_field = 'djnago.db.models.BigAutoField'
    name = 'apps.api_logs'
    verbose_name = 'API Logs'
