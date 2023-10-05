from django.utils import timezone
from rest_framework import serializers


def validate_year(value):
    """Проверяет, что год выпуска не будущее время."""
    year = timezone.now().year
    if value > year:
        raise serializers.ValidationError('Проверьте год выпуска!')
