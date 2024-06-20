from django.contrib import admin

from users.models import User, Tag


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'gender', 'age', 'role', 'email_confirmed')
    list_filter = ('gender', 'role', 'email_confirmed')
    search_fields = ('username', 'email', 'description')
    readonly_fields = ('email_confirmed',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личная информация', {'fields': ('email', 'gender', 'age', 'photo')}),
        ('Дополнительная информация', {'fields': ('description', 'tags')}),
        ('Разрешения', {'fields': ('role', 'email_confirmed', 'is_staff', 'is_active')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    filter_horizontal = ('tags',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
