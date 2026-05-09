from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from blog.models import BlogPost

User = get_user_model()


class BlogPostModelTest(TestCase):
    """Тесты модели BlogPost"""

    def setUp(self):
        self.post = BlogPost.objects.create(
            title="Тестовая статья", content="Содержание тестовой статьи", is_published=True, views_count=0
        )

    def test_blog_post_creation(self):
        """Проверка создания статьи"""
        self.assertEqual(self.post.title, "Тестовая статья")
        self.assertEqual(str(self.post), "Тестовая статья")
        self.assertEqual(self.post.views_count, 0)
        self.assertTrue(self.post.is_published)

    def test_views_count_increment(self):
        """Проверка увеличения счетчика просмотров"""
        initial_views = self.post.views_count
        self.client.get(reverse("blog:blogpost_detail", args=[self.post.pk]))
        self.post.refresh_from_db()
        self.assertEqual(self.post.views_count, initial_views + 1)

    def test_email_on_100_views(self):
        """Проверка отправки email при 100 просмотрах"""
        self.post.views_count = 99
        self.post.save()

        # 100-й просмотр
        self.client.get(reverse("blog:blogpost_detail", args=[self.post.pk]))

        # Проверяем, что email был отправлен
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("достигла 100 просмотров", mail.outbox[0].subject)

    def test_published_filter(self):
        """Фильтр только опубликованных статей"""
        BlogPost.objects.create(title="Черновик", content="Не опубликовано", is_published=False)

        BlogPost.objects.create(title="Опубликовано 2", content="Вторая статья", is_published=True)

        published_posts = BlogPost.objects.filter(is_published=True)
        self.assertEqual(published_posts.count(), 2)  # Одна из setUp + новая


class BlogPostListViewTest(TestCase):
    """Тесты списка статей"""

    def setUp(self):
        # Создаем 10 статей для проверки пагинации
        for i in range(10):
            BlogPost.objects.create(
                title=f"Статья {i}", content=f"Содержание {i}", is_published=True if i % 2 == 0 else False
            )

    def test_only_published_shown(self):
        """Отображаются только опубликованные статьи"""
        response = self.client.get(reverse("blog:blogpost_list"))
        self.assertEqual(response.status_code, 200)

        for post in response.context["blogs"]:
            self.assertTrue(post.is_published)

    def test_pagination(self):
        """Пагинация статей (6 на страницу)"""
        response = self.client.get(reverse("blog:blogpost_list"))
        # Ожидаем до 6 статей на странице
        self.assertLessEqual(len(response.context["blogs"]), 6)


class BlogPostPermissionsTest(TestCase):
    """Тесты прав доступа к блогу"""

    def setUp(self):
        # Создаем группу "Content manager"
        self.group, _ = Group.objects.get_or_create(name="Content manager")

        # Создаем пользователя с правами
        self.user = User.objects.create_user(email="manager@test.com", password="manager123")
        self.user.groups.add(self.group)

        # Создаем обычного пользователя
        self.regular_user = User.objects.create_user(email="user@test.com", password="user123")

        self.post = BlogPost.objects.create(title="Тестовая статья", content="Содержание", is_published=True)

        self.client.login(email="manager@test.com", password="manager123")

    def test_create_permission(self):
        """Только контент-менеджер может создавать статьи"""
        response = self.client.get(reverse("blog:blogpost_create"))
        self.assertEqual(response.status_code, 200)

        # Обычный пользователь не может создать
        self.client.login(email="user@test.com", password="user123")
        response2 = self.client.get(reverse("blog:blogpost_create"))
        self.assertEqual(response2.status_code, 403)

    def test_update_permission(self):
        """Только контент-менеджер может редактировать статьи"""
        response = self.client.get(reverse("blog:blogpost_update", args=[self.post.pk]))
        self.assertEqual(response.status_code, 200)

        # Обычный пользователь не может редактировать
        self.client.login(email="user@test.com", password="user123")
        response2 = self.client.get(reverse("blog:blogpost_update", args=[self.post.pk]))
        self.assertEqual(response2.status_code, 403)

    def test_delete_permission(self):
        """Только контент-менеджер может удалять статьи"""
        response = self.client.post(reverse("blog:blogpost_delete", args=[self.post.pk]))
        self.assertRedirects(response, reverse("blog:blogpost_list"))
        self.assertFalse(BlogPost.objects.filter(pk=self.post.pk).exists())
