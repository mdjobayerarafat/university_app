from django.contrib import admin
from .models import ChatMessage, FAQ

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user_message', 'bot_response', 'created_at')
    search_fields = ('user_message', 'bot_response')
    readonly_fields = ('created_at',)

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'answer', 'created_at', 'updated_at')
    search_fields = ('question', 'answer')
    readonly_fields = ('created_at', 'updated_at')