import re

from rest_framework import serializers
from rest_framework.fields import CharField, EmailField
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Category, Genre, GenreTitle, Title
from users.models import CustomUser


class TitleSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Title


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'slug')
        model = Genre

        
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
