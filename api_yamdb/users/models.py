import uuid

from django.contrib.auth.models import AbstractUser
from django.db.models import EmailField, UUIDField


class CustomUser(AbstractUser):
    email = EmailField(
        'Электронная почта',
        max_length=30,
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
