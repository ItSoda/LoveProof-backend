from django.contrib import admin

from chat.models import Chat, Message


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display =('id', 'participants_list', 'created_at')
    filter_horizontal = ('participants',)
    date_hierarchy = 'created_at'

    def participants_list(self, obj):
        return ", ".join([participant.username for participant in obj.participants.all()])

    participants_list.short_description = 'Участники'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'user', 'created_at')
    list_filter = ('chat', 'user')
    search_fields = ('message', 'user__username')
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('chat', 'user')
