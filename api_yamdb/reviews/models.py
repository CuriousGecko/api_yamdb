from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField(max_length=256, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        related_name='titles', blank=True, null=True)
    genre = models.ManyToManyField(
        Genre, through='GenreTitle',
        related_name='titles_of_genre'
    )

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.ForeignKey(Title, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(models.Model):
    """
    Модель для хранения обзоров на записи.
    Связь с Title через поле reviews.
    """
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    text = models.TextField(
        'Текст обзора',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    score = models.IntegerField(
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ]
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


class Comment(models.Model):
    """
    Модель для хранения комментариев к обзорам.
    Связь с Review через поле comments.
    """
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text


# class AggregatedRating(models.Model):
#     """
#     Модель для хранения среднего рейтинга для записи.
#     Связь с Title через поле rating.
#     """
#     title = models.ForeignKey(
#         Title,
#         on_delete=models.CASCADE,
#         related_name='rating'
#     )
#     average_score = models.FloatField(default=0)

#     def __str__(self):
#         return str(self.average_score)

#     # Этот метод должен вызываться во view-функции?
#     @classmethod
#     def count_average(cls, title):
#         scores = Review.objects.filter(
#             title_id=title).values_list('score', flat=True)
#         if scores:
#             average_score = sum(scores) / len(scores)
#         else:
#             average_score = 0
#         title.rating = average_score
#         title.save()
#         return average_score
