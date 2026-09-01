from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description', 'owner__email')
    readonly_fields = ('created_at', 'updated_at')