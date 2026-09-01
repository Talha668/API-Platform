from django.contrib import admin
from .models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'scope', 'key_prefix', 'is_active', 'last_used_at')
    list_filter = ('scope', 'is_active', 'created_at')
    search_fields = ('name', 'project__name', 'key_prefix')
    readonly_fields = ('key_hash', 'key_prefix', 'created_at', 'updated_at')