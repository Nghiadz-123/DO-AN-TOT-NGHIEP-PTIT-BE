from django.contrib import admin

from .models import Connection


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ['requester', 'addressee', 'status', 'job', 'created_at', 'responded_at']
    list_filter = ['status']
    search_fields = ['requester__email', 'requester__full_name', 'addressee__email', 'addressee__full_name']
    raw_id_fields = ['requester', 'addressee', 'job']
    readonly_fields = ['created_at', 'updated_at', 'responded_at']
