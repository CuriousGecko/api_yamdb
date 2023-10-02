from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.fields import CharField
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer

from reviews.models import Category, Comment, Genre, Review, Title

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


class TitleSerializerGet(serializers.ModelSerializer):
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
        """Считает среднюю оценку."""
        rating = Title.objects.filter(
            id=obj.id).aggregate(avg=Avg('reviews__score'))
        return rating.get('avg')


class TitleSerializerPost(TitleSerializerGet):
    category = SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    genre = SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
    )


class ReviewSerializer(ModelSerializer):
    author = SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    title = serializers.SerializerMethodField()

    def get_title(self, obj):
        return self.context['title']

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

    def validate(self, data):
        """
        Ограничение уникальности для соблюдения правила
        "один пользователь - одна заметка к записи".
        """
        if self.context['method'] == 'POST':
            author = self.context['request'].user
            title = self.context['title']
            existing_reviews = Review.objects.filter(
                author=author,
                title=title,
            )
            if existing_reviews.exists():
                raise serializers.ValidationError(
                    'Вы уже оставляли заметку к этой записи!'
                )
        return data


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


class SignUpSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
        )

    def validate(self, data):
        """Проверит схожесть аккаунта пользователя в БД и данных запроса."""
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


class NotAdminUsersSerializer(ForAdminUsersSerializer):
    role = CharField(
        read_only=True,
    )
