from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserModelTest(TestCase):
    """Тесты модели пользователя"""

    def test_create_user(self):
        """Создание обычного пользователя"""
        user = User.objects.create_user(email="user@test.com", password="testpass123")
        self.assertEqual(user.email, "user@test.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Создание суперпользователя"""
        admin = User.objects.create_superuser(email="admin@test.com", password="adminpass123")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_user_str_method(self):
        """Проверка строкового представления"""
        user = User.objects.create_user(email="test@test.com", password="pass")
        self.assertEqual(str(user), "test@test.com")

    def test_email_unique(self):
        """Email должен быть уникальным"""
        User.objects.create_user(email="duplicate@test.com", password="pass1")
        with self.assertRaises(Exception):
            User.objects.create_user(email="duplicate@test.com", password="pass2")


class UserRegistrationTest(TestCase):
    """Тесты регистрации пользователя"""

    def test_registration_page(self):
        """Страница регистрации доступна"""
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")

    def test_successful_registration(self):
        """Успешная регистрация"""
        response = self.client.post(
            reverse("users:register"),
            {"email": "newuser@test.com", "password1": "StrongPass123!", "password2": "StrongPass123!"},
        )

        self.assertRedirects(response, reverse("users:login"))
        self.assertTrue(User.objects.filter(email="newuser@test.com").exists())

        # Проверка отправки приветственного письма
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Приветственное письмо", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, ["newuser@test.com"])

    def test_registration_with_existing_email(self):
        """Регистрация с уже существующим email"""
        User.objects.create_user(email="existing@test.com", password="pass123")

        response = self.client.post(
            reverse("users:register"),
            {"email": "existing@test.com", "password1": "StrongPass123!", "password2": "StrongPass123!"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "already exists")

    def test_registration_password_mismatch(self):
        """Пароли не совпадают"""
        response = self.client.post(
            reverse("users:register"),
            {"email": "newuser@test.com", "password1": "Pass123!", "password2": "DifferentPass123!"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "password")


class UserLoginLogoutTest(TestCase):
    """Тесты входа и выхода"""

    def setUp(self):
        self.user = User.objects.create_user(email="testuser@test.com", password="testpass123")

    def test_login_page(self):
        """Страница входа доступна"""
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, 200)

    def test_successful_login(self):
        """Успешный вход"""
        response = self.client.post(
            reverse("users:login"), {"username": "testuser@test.com", "password": "testpass123"}
        )
        self.assertRedirects(response, "/")

    def test_login_wrong_password(self):
        """Неверный пароль"""
        response = self.client.post(
            reverse("users:login"), {"username": "testuser@test.com", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a correct")

    def test_logout(self):
        """Выход из системы"""
        self.client.login(email="testuser@test.com", password="testpass123")
        response = self.client.post(reverse("users:logout"))
        self.assertRedirects(response, "/")


class UserProfileTest(TestCase):
    """Тесты профиля пользователя"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="profile@test.com", password="profilepass123", phone_number="+79991234567", country="Россия"
        )
        self.client.login(email="profile@test.com", password="profilepass123")

    def test_profile_page_accessible(self):
        """Страница профиля доступна авторизованному пользователю"""
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile_form.html")

    def test_profile_page_redirects_for_anonymous(self):
        """Неавторизованный пользователь перенаправляется на логин"""
        self.client.logout()
        response = self.client.get(reverse("users:profile"))
        self.assertRedirects(response, f"{reverse('users:login')}?next=/users/profile/")

    def test_update_profile(self):
        """Обновление профиля"""
        response = self.client.post(
            reverse("users:profile"), {"phone_number": "+79876543210", "country": "Беларусь", "avatar": ""}
        )
        self.assertRedirects(response, reverse("catalog:home"))

        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, "+79876543210")
        self.assertEqual(self.user.country, "Беларусь")
