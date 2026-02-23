from typing import Any

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Создаёт группу модератор продуктов."""

    help = "Create group moderator of products"

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """Создает группу модератор продуктов."""

        group, created = Group.objects.get_or_create(name="Moderator of products")
        delete_product = Permission.objects.get(codename="delete_product")
        unpublish_product = Permission.objects.get(codename="can_unpublish_product")
        if created:
            group.permissions.add(delete_product)
            group.permissions.add(unpublish_product)
            group.save()
            self.stdout.write(self.style.SUCCESS("Successfully created group with permission"))
        else:
            self.stdout.write(self.style.WARNING(f"Group - {group} already exist"))
