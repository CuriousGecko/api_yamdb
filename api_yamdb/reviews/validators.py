from datetime import date

from rest_framework import serializers


def validate_year(value):
    """Проверяет, что год выпуска не будущее время."""
    year = date.today().year
    if value > year:
        raise serializers.ValidationError('Проверьте год выпуска!')
