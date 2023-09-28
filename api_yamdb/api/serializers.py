import re

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.fields import CharField
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from datetime import date
from reviews.models import Category, Genre, GenreTitle, Title

User = get_user_model()

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'name',
            'slug',
        )
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'name',
            'slug',
        )
        model = Genre
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    category = SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )
    # rating = None

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
        )
        # Добавить - 'rating',
        model = Title

    def validate_year(self, value):
        """Проверяет, что год выпуска не будущее время."""
        year = date.today().year
        if value > year:
            raise serializers.ValidationError('Проверьте год выпуска!')
        return value

# aggregate - Для рейтинга

        
class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
    )
    email = serializers.EmailField(
        max_length=254,
    )

    def validate_username(self, value):
        if re.search(r'^[\w.@+-]+\Z', value) is None:
            raise serializers.ValidationError(
                f'Имя пользователя {value} содержит недопустимые символы.'
            )
        if value == 'me':
            raise serializers.ValidationError(
                f'Недопустимое имя пользователя: me.'
            )
        return value

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if (
            User.objects.filter(username=username).exists()
            and User.objects.get(username=username).email != email
        ):
            raise serializers.ValidationError(
                f'Пользователь с именем {username} уже существует.'
            )
        if (
            User.objects.filter(email=email).exists()
            and User.objects.get(email=email).username != username
        ):
            raise serializers.ValidationError(
                f'Пользователь с почтовым адресом {email} '
                f'уже существует.'
            )
        return data


class TokenSerializer(serializers.Serializer):
    username = CharField(
        max_length=150,
    )
    confirmation_code = CharField()
