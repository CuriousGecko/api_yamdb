import uuid

from django.contrib.auth.models import AbstractUser
from django.db.models import (CharField, EmailField, TextChoices, TextField,
                              UUIDField)

from users.validators import validate_username


class CustomUser(AbstractUser):
    class Roles(TextChoices):
        USER = 'user'
        MODERATOR = 'moderator'
        ADMIN = 'admin'

    role = CharField(
        max_length=255,
        default=Roles.USER,
        choices=Roles.choices,
    )
    username = CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        validators=[validate_username],
    )
    first_name = CharField(
        'Имя',
        max_length=150,
        blank=True,
    )
    last_name = CharField(
        'Фамилия',
        max_length=150,
        blank=True,
    )
    bio = TextField(
        'О пользователе',
        blank=True,
    )
    email = EmailField(
        'Электронная почта',
        max_length=254,
        unique=True,
        blank=False,
        null=False,
    )
    confirmation_code = UUIDField(
        'Код подтверждения',
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
