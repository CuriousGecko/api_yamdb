from datetime import date
from reviews.models import Title, Category, Genre, GenreTitle
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.serializers import ModelSerializer
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



class SignUpSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
        )

# aggregate - Для рейтинга
