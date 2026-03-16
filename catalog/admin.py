from django.contrib import admin

from .models import Category, ContactInfo, Product


@admin.register(Category)
class AdminCategory(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
    )


@admin.register(Product)
class AdminProduct(admin.ModelAdmin):
    list_display = ("id", "name", "price", "category", "is_published", "owner")
    list_filter = ("category",)
    search_fields = ("name", "description", "is_published", "owner")


@admin.register(ContactInfo)
class AdminContact(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "phone",
    )
    search_fields = (
        "name",
        "email",
    )
