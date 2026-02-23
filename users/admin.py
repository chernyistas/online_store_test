from django.contrib import admin

from .models import User


@admin.register(User)
class AdminProduct(admin.ModelAdmin):
    list_display = ("id", "email")
