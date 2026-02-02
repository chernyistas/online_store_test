from django.contrib import admin

from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """Настройки отображения модели BlogPost в админ-панели"""

    list_display = ("title", "is_published", "views_count", "created_at")
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "content")
