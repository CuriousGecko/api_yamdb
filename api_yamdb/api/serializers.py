from django.db.models import Avg
from reviews.models import (
    Title, Category, Genre, Review, Comment
)
from rest_framework import serializers
# from rest_framework.relations import SlugRelatedField
# from rest_framework.validators import UniqueTogetherValidator
from rest_framework.serializers import ModelSerializer
from users.models import CustomUser


class TitleSerializer(serializers.ModelSerializer):
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


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'slug')
        model = Genre


class SignUpSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
        )


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


# class AggregatedRatingSerializer(ModelSerializer):
#     class Meta:
#         model = AggregatedRating
#         fields = (
#             'title',
#             'average_score'
#         )
