from django.contrib import admin

from community.models import Post, Comment, Like, Category, Report


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'header', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('header', 'text')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'comment', 'created_at')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    search_fields = ('title',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post', 'comment', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'post__title', 'comment__text', 'text']
    list_per_page = 20
    readonly_fields = ['created_at']

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'post', 'comment', 'text', 'status')
        }),
        ('Временные метки', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
