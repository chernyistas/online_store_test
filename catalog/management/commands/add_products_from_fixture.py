from typing import Any

from django.core.management import call_command
from django.core.management.base import BaseCommand

from catalog.models import Category, Product


class Command(BaseCommand):
    """Удаляет данные и загружает из фикстуры products_fixture.json."""

    help = "Delete and add products from fixture to the database"

    def handle(self, *args: Any, **kwargs: Any) -> None:
        """Очищает БД и загружает фикстуру."""

        Product.objects.all().delete()
        Category.objects.all().delete()

        call_command("loaddata", "products_fixture.json")
        self.stdout.write(self.style.SUCCESS("Successfully loaded data from fixture"))
