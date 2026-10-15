from django.contrib import admin

from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    fields = ['sender', 'body', 'created_at', 'read_at']
    readonly_fields = fields
    can_delete = False


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['user_a', 'user_b', 'last_message_at', 'created_at']
    search_fields = ['user_a__email', 'user_a__full_name', 'user_b__email', 'user_b__full_name']
    raw_id_fields = ['user_a', 'user_b']
    readonly_fields = ['last_message_at', 'created_at', 'updated_at']
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'sender', 'short_body', 'created_at', 'read_at']
    search_fields = ['body', 'sender__email']
    raw_id_fields = ['conversation', 'sender']

    @admin.display(description='nội dung')
    def short_body(self, obj):
        return obj.body[:80]
