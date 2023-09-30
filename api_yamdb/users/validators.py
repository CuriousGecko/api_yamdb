import re

from rest_framework import serializers


def validate_username(value):
    """Проверит наличие недопустимых символов в имени пользователя."""
    if re.search(r'^[\w.@+-]+\Z', value) is None:
        raise serializers.ValidationError(
            f'Имя пользователя {value} содержит недопустимые символы.',
        )
    if value == 'me':
        raise serializers.ValidationError(
            f'Недопустимое имя пользователя: me.'
        )
