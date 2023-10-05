from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from api_yamdb.constants import (MAX_LENGHT_EMAIL, MAX_LENGHT_NAME,
                                 MAX_LENGHT_NAME_USER)


class CustomUser(AbstractUser):
    """Переопределенная модель пользователя."""

    class Roles(models.TextChoices):
        USER = 'user'
        MODERATOR = 'moderator'
        ADMIN = 'admin'

    role = models.CharField(
        'Роль',
        max_length=MAX_LENGHT_NAME,
        default=Roles.USER,
        choices=Roles.choices,
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LENGHT_NAME_USER,
        blank=True,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LENGHT_NAME_USER,
        blank=True,
    )
    bio = models.TextField(
        'О пользователе',
        blank=True,
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=MAX_LENGHT_EMAIL,
        unique=True,
        blank=False,
        null=False,
        error_messages={
            'unique': 'Пользователь с такой электронной почтой уже существует.'
        },
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def clean(self):
        super().clean()
        if self.username == 'me':
            raise ValidationError(
                'Недопустимое имя пользователя: me.'
            )

    @property
    def is_admin_or_superuser(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    def __str__(self):
        return self.username
