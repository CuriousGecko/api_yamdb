from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from datetime import date
from django.db.models import Avg
from reviews.models import (
    Title, Category, Genre, Review, Comment
)
from rest_framework.serializers import ModelSerializer

User = get_user_model()


class TitleSerializer(serializers.ModelSerializer):
    category = SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    genre = SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'name',
            'year',
            'category',
            'genre',
            'rating'
        )
        model = Title

    def get_rating(self, obj):
        rating = Title.objects.filter(
            id=obj.id).aggregate(avg=Avg('reviews__score'))
        return rating.get('avg')

    def validate_year(self, value):
        """Проверяет, что год выпуска не будущее время."""
        year = date.today().year
        if value > year:
            raise serializers.ValidationError('Проверьте год выпуска!')
        return value


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


class ReviewSerializer(ModelSerializer):
    class Meta:
        model = Review
        fields = (
            'title',
            'text',
            'author',
            'score',
            'pub_date'
        )

    def validate(self, data):
        author = data['author']
        title = data['title']
        excisting_reviews = Review.objects.filter(
            author=author, title=title
        )
        if excisting_reviews.exists():
            raise serializers.ValidationError(
                'Вы уже оставляли заметку к этой записи!'
            )
        return data


class CommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            'id',
            'text',
            'author',
            'pub_date'
        )
