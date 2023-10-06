from django.contrib.auth.models import AbstractUser
from django.db import models

from api_yamdb.constants import MAX_LENGHT_EMAIL, MAX_LENGHT_ROLE


class CustomUser(AbstractUser):
    """Переопределенная модель пользователя."""

    class Roles(models.TextChoices):
        USER = 'user'
        MODERATOR = 'moderator'
        ADMIN = 'admin'

    role = models.CharField(
        'Роль',
        max_length=MAX_LENGHT_ROLE,
        default=Roles.USER,
        choices=Roles.choices,
    )
    bio = models.TextField(
        'О пользователе',
        blank=True,
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=MAX_LENGHT_EMAIL,
        unique=True,
        error_messages={
            'unique': 'Пользователь с такой электронной почтой уже существует.'
        },
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == 'moderator'
