from django.contrib import admin

from .models import Invitation


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ['job', 'candidate', 'status', 'sender', 'created_at', 'read_at', 'responded_at']
    list_filter = ['status']
    search_fields = ['job__title', 'candidate__user__email', 'candidate__user__full_name']
    raw_id_fields = ['job', 'candidate', 'sender', 'application']
    readonly_fields = ['created_at', 'updated_at', 'read_at', 'responded_at']
