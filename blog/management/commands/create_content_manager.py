from typing import Any

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from blog.models import BlogPost


class Command(BaseCommand):
    """Создаёт группу Контент-менеджер."""

    help = "Create content manager group with blog permissions"

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """Создает группу Контент-менеджер."""
        group, created = Group.objects.get_or_create(name="Content manager")

        if created:
            content_type = ContentType.objects.get_for_model(BlogPost)
            add_blogpost = Permission.objects.get(codename="add_blogpost", content_type=content_type)
            change_blogpost = Permission.objects.get(codename="change_blogpost", content_type=content_type)
            delete_blogpost = Permission.objects.get(codename="delete_blogpost", content_type=content_type)
            view_blogpost = Permission.objects.get(codename="view_blogpost", content_type=content_type)

            group.permissions.add(add_blogpost, change_blogpost, delete_blogpost, view_blogpost)
            group.save()
            self.stdout.write(self.style.SUCCESS("Successfully created group with permission"))
        else:
            self.stdout.write(self.style.WARNING(f"Group - {group} already exist"))
