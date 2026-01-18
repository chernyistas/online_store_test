from typing import Any, Dict

from django.core.management import BaseCommand

from catalog.models import Category, Product


class Command(BaseCommand):
    """Добавляет тестовые продукты в категорию 'Процессоры'."""

    help = "Add test products to database"

    def handle(self, *args: Any, **options: Dict[str, Any]) -> None:
        """Создаёт категорию и продукты, избегая дублей."""

        category, created = Category.objects.get_or_create(
            name="Процессоры", defaults={"description": "Комплектующие"}
        )

        products_data: list[Dict[str, Any]] = [
            {"name": "AMD 9800X3D", "description": "Gaming CPU 5.2GHz", "category": category, "price": 55000},
            {"name": "Intel i9-14900K", "description": "16 cores workstation", "category": category, "price": 75000},
            {"name": "Ryzen 7 7800X3D", "description": "Best for gaming", "category": category, "price": 45000},
        ]

        for data in products_data:
            product, created = Product.objects.get_or_create(**data)

            if created:
                self.stdout.write(self.style.SUCCESS(f'Добавлено {product.name} в "{category.name}"'))
            else:
                self.stdout.write(self.style.WARNING(f'Продукты {product.name} уже есть в "{category.name}"'))
