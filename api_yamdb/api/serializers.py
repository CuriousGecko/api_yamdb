import re

from rest_framework import serializers
from rest_framework.fields import CharField, EmailField
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from datetime import date
from reviews.models import Category, Genre, GenreTitle, Title
from users.models import CustomUser


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    category = SlugRelatedField(slug_field='slug', queryset=Category.objects.all())
    genre = serializers.SlugRelatedField(slug_field='slug', queryset=Genre.objects.all(), many=True)
    # rating = None

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
        # Добавить - 'rating',
        model = Title

    def validate_year(self, value):
        """Проверяет, что год выпуска не будущее время."""
        year = date.today().year
        if value > year:
            raise serializers.ValidationError('Проверьте год выпуска!')
        return value

# aggregate - Для рейтинга

        
class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
        )

    def validate_username(self, value):
        if re.search(r'^[\w@./+\-]+$', value) is None:
            raise serializers.ValidationError(
                f'Имя пользователя {value} содержит недопустимые символы.'
            )
        if value == 'me':
            raise serializers.ValidationError(
                f'Недопустимое имя пользователя: me.'
            )
        return value


class TokenSerializer(serializers.Serializer):
    username = CharField(
        max_length=150,
    )
    confirmation_code = CharField()