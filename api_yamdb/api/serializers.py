import re
from datetime import date

from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.fields import CharField
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer

from reviews.models import Category, Comment, Genre, Review, Title

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
            'id',
            'name',
            'year',
            'category',
            'genre',
            'rating',
        )
        model = Title

    def get_rating(self, obj):
        """Считает среднюю оценку."""
        rating = Title.objects.filter(
            id=obj.id
        ).aggregate(
            avg=Avg('reviews__score')
        )
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
            'pub_date',
        )

    def validate(self, data):
        """Не позволяет автору прокомментировать одну и ту же запись."""
        author = data['author']
        title = data['title']
        existing_reviews = Review.objects.filter(
            author=author, title=title
        )
        if existing_reviews.exists():
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
            'pub_date',
        )


class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
    )
    email = serializers.EmailField(
        max_length=254,
    )

    def validate_username(self, value):
        """Проверит наличие недопустимых символов в имени пользователя."""
        if re.search(r'^[\w.@+-]+\Z', value) is None:
            raise serializers.ValidationError(
                f'Имя пользователя {value} содержит недопустимые символы.',
            )
        if value == 'me':
            raise serializers.ValidationError(
                f'Недопустимое имя пользователя: me.'
            )
        return value

    def validate(self, data):
        """Проверит наличие учетной записи пользователя в БД."""
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


class ForAdminUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'role',
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
        )

    def validate_username(self, value):
        """Проверит наличие недопустимых символов в имени пользователя."""
        if re.search(r'^[\w.@+-]+\Z', value) is None:
            raise serializers.ValidationError(
                f'Имя пользователя {value} содержит недопустимые символы.',
            )
        if value == 'me':
            raise serializers.ValidationError(
                f'Недопустимое имя пользователя: me.'
            )
        return value


class NotAdminUsersSerializer(ForAdminUsersSerializer):
    role = CharField(read_only=True,)
