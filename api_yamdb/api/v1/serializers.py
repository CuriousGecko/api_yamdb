from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.fields import CharField
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name',
            'slug',
        )
        model = Category
        lookup_url_kwargs = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'name',
            'slug',
        )
        model = Genre
        lookup_field = 'slug'


class TitleGetSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    genre = GenreSerializer(
        read_only=True,
        many=True,
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id',
            'name',
            'description',
            'year',
            'category',
            'genre',
            'rating',
        )
        model = Title

    def get_rating(self, obj):
        # return self.context['rating']

        return self.context['rating'].get('avg')
    #     """Считает среднюю оценку."""
    #     rating = Title.objects.filter(
    #         id=obj.id
    #     ).aggregate(
    #         avg=Avg('reviews__score')
    #     )
    #     return rating.get('avg')


class TitlePostSerializer(TitleGetSerializer):
    category = SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    genre = SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )


class CurrentTitleDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['view'].kwargs['title_id']


class ReviewSerializer(ModelSerializer):
    author = SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    title = serializers.PrimaryKeyRelatedField(
        queryset=Title.objects.all(),
        default=CurrentTitleDefault()
    )

    class Meta:
        model = Review
        fields = (
            'id',
            'title',
            'text',
            'author',
            'score',
            'pub_date',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('title', 'author'),
                message='Вы уже оставляли отзыв к этому произведению.'
            )
        ]

    # def validate(self, data):
    #     """
    #     Ограничение уникальности для соблюдения правила
    #     "один пользователь - одна заметка к записи".
    #     """
    #     if self.context['request'].method == 'POST':
    #         author = self.context['request'].user
    #         title = self.context['view'].kwargs['title_id']
    #         existing_reviews = Review.objects.filter(
    #             author=author,
    #             title=title,
    #         )
    #         if existing_reviews.exists():
    #             raise serializers.ValidationError(
    #                 'Вы уже оставляли заметку к этой записи!'
    #             )
    #     return data


class CommentSerializer(ModelSerializer):
    author = SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = (
            'id',
            'text',
            'author',
            'pub_date',
        )


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
        )

    def validate(self, data):
        instance = self.Meta.model(**data)
        instance.clean()
        return data


class TokenSerializer(serializers.Serializer):
    username = CharField(
        max_length=150,
    )
    confirmation_code = CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Тесты требуют роль).
        fields = (
            'role',
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
        )

    def validate(self, data):
        instance = self.Meta.model(**data)
        instance.clean()
        return data
