from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="Почта", help_text="Введите почту")
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Введите номер телефона",
        verbose_name="Номер телефона",
    )
    country = models.CharField(max_length=30, verbose_name="Страна", blank=True, null=True, help_text="Введите страну")
    avatar = models.ImageField(
        upload_to="users/avatar/", null=True, blank=True, verbose_name="Аватар", help_text="Добавьте аватар"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
