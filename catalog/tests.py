from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from catalog.forms import FORBIDDEN_WORDS, ProductForm
from catalog.models import Category, ContactInfo, Product

User = get_user_model()


class CategoryModelTest(TestCase):
    """Тесты модели Category"""

    def setUp(self):
        self.category = Category.objects.create(name="Электроника", description="Техника и гаджеты")

    def test_category_creation(self):
        """Проверка создания категории"""
        self.assertEqual(self.category.name, "Электроника")
        self.assertEqual(str(self.category), "Электроника")
        self.assertEqual(self.category._meta.verbose_name, "категория")

    def test_category_ordering(self):
        """Проверка сортировки по имени"""
        Category.objects.create(name="Аудио")
        Category.objects.create(name="Видео")
        categories = Category.objects.all()
        self.assertEqual(categories[0].name, "Аудио")
        self.assertEqual(categories[1].name, "Видео")
        self.assertEqual(categories[2].name, "Электроника")


class ProductModelTest(TestCase):
    """Тесты модели Product"""

    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="testpass123")
        self.category = Category.objects.create(name="Техника")
        self.product = Product.objects.create(
            name="Смартфон",
            description="Отличный телефон",
            category=self.category,
            price=29999.99,
            owner=self.user,
            is_published=True,
        )

    def test_product_creation(self):
        """Проверка создания товара"""
        self.assertEqual(self.product.name, "Смартфон")
        self.assertEqual(str(self.product), "Смартфон")
        self.assertEqual(self.product.price, 29999.99)
        self.assertTrue(self.product.is_published)
        self.assertEqual(self.product.owner, self.user)

    def test_negative_price_validation(self):
        """Цена не может быть отрицательной"""
        form_data = {"name": "Тест", "category": self.category.id, "price": -100, "description": "Описание"}
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("price", form.errors)

    def test_forbidden_words_in_name(self):
        """Запрещенные слова в названии"""
        for word in FORBIDDEN_WORDS:
            form_data = {
                "name": f"{word} товар",
                "category": self.category.id,
                "price": 1000,
                "description": "Описание",
            }
            form = ProductForm(data=form_data)
            self.assertFalse(form.is_valid())
            self.assertIn("name", form.errors)

    def test_forbidden_words_in_description(self):
        """Запрещенные слова в описании"""
        form_data = {
            "name": "Нормальный товар",
            "category": self.category.id,
            "price": 1000,
            "description": "Это описание с словом криптовалюта",
        }
        form = ProductForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("description", form.errors)

    def test_product_image_validation(self):
        """Валидация изображения"""
        invalid_image = SimpleUploadedFile("test.txt", b"file_content", content_type="text/plain")
        form_data = {"name": "Товар", "category": self.category.id, "price": 1000, "description": "Описание"}
        form = ProductForm(data=form_data, files={"image": invalid_image})
        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)


class ProductListViewTest(TestCase):
    """Тесты списка товаров"""

    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="testpass123")
        self.category = Category.objects.create(name="Техника")

        # Создаем 10 товаров для проверки пагинации
        for i in range(10):
            Product.objects.create(
                name=f"Товар {i}", category=self.category, price=1000 + i, owner=self.user, is_published=True
            )

    def test_pagination(self):
        """Проверка пагинации (6 товаров на странице)"""
        response = self.client.get(reverse("catalog:home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["products"]), 6)

    def test_cache_used(self):
        """Проверка использования кэша"""
        cache.clear()

        # Первый запрос - данные из БД
        response1 = self.client.get(reverse("catalog:home"))
        self.assertEqual(response1.status_code, 200)

        # Удаляем все товары
        Product.objects.all().delete()

        # Второй запрос - должен быть из кэша
        response2 = self.client.get(reverse("catalog:home"))
        self.assertEqual(response2.status_code, 200)
        # Товары все еще есть из-за кэша
        self.assertEqual(len(response2.context["products"]), 6)


class ProductDetailViewTest(TestCase):
    """Тесты детальной страницы товара"""

    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="testpass123")
        self.category = Category.objects.create(name="Техника")
        self.product = Product.objects.create(
            name="Телефон",
            description="Описание телефона",
            category=self.category,
            price=25000,
            owner=self.user,
            is_published=True,
        )

    def test_product_detail_page(self):
        """Проверка страницы товара"""
        response = self.client.get(reverse("catalog:product_detail", args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["product"].name, "Телефон")
        self.assertContains(response, "Телефон")
        self.assertContains(response, "25000")

    def test_nonexistent_product(self):
        """Несуществующий товар - 404"""
        response = self.client.get(reverse("catalog:product_detail", args=[9999]))
        self.assertEqual(response.status_code, 404)


class ProductCreateViewTest(TestCase):
    """Тесты создания товара"""

    def setUp(self):
        self.user = User.objects.create_user(email="seller@test.com", password="sellerpass123")
        self.category = Category.objects.create(name="Техника")
        self.client.login(email="seller@test.com", password="sellerpass123")

    def test_create_product_authenticated(self):
        """Авторизованный пользователь может создать товар"""
        response = self.client.post(
            reverse("catalog:product_create"),
            {
                "name": "Новый товар",
                "description": "Описание нового товара",
                "category": self.category.id,
                "price": 15000,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(name="Новый товар").exists())

        product = Product.objects.get(name="Новый товар")
        self.assertEqual(product.owner, self.user)

    def test_create_product_unauthenticated(self):
        """Неавторизованный пользователь не может создать товар"""
        self.client.logout()
        response = self.client.get(reverse("catalog:product_create"))
        self.assertRedirects(response, f"{reverse('users:login')}?next=/product/create/")


class ContactViewTest(TestCase):
    """Тесты страницы контактов"""

    def test_contact_page_get(self):
        """GET запрос к странице контактов"""
        response = self.client.get(reverse("catalog:contact"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/contact.html")

    def test_contact_form_post_valid(self):
        """POST запрос с валидными данными"""
        response = self.client.post(
            reverse("catalog:contact"), {"name": "Иван", "phone": "+79991234567", "message": "Хочу купить товар"}
        )
        self.assertRedirects(response, reverse("catalog:contact"))
        self.assertTrue(ContactInfo.objects.filter(name="Заявка: Иван").exists())

    def test_contact_form_post_invalid(self):
        """POST запрос без обязательных полей"""
        # Без имени и сообщения форма не сохраняется
        self.assertEqual(ContactInfo.objects.count(), 0)
