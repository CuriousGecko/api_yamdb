from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from api_yamdb.constants import (
    MAX_LENGHT_NAME, MAX_LENGHT_SLUG, MAX_LENGTH_STR
)
from reviews.validators import validate_year

User = get_user_model()


class Category(models.Model):
    """Модель для хранения категорий."""

    name = models.CharField(
        'Категория',
        max_length=MAX_LENGHT_NAME,
    )
    slug = models.SlugField(
        'Идентификатор',
        max_length=MAX_LENGHT_SLUG,
        unique=True,
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name[:MAX_LENGTH_STR]


class Genre(models.Model):
    """Модель для хранения жанров."""

    name = models.CharField(
        'Жанр',
        max_length=MAX_LENGHT_NAME,
    )
    slug = models.SlugField(
        'Идентификатор',
        max_length=MAX_LENGHT_SLUG,
        unique=True,
    )

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name[:MAX_LENGTH_STR]


class Title(models.Model):
    """Модель для хранения записей произведений."""

    name = models.CharField(
        'Название',
        max_length=MAX_LENGHT_NAME,
    )
    year = models.PositiveSmallIntegerField(
        'Год',
        validators=[validate_year],
    )
    description = models.TextField(
        'Описание',
        max_length=MAX_LENGHT_NAME,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True,
        verbose_name='Категория',
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles_of_genre',
        verbose_name='Жанр',
    )

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name[:MAX_LENGTH_STR]


class Review(models.Model):
    """Модель для хранения обзоров на произведения."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
    )
    text = models.TextField(
        'Текст обзора',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    score = models.IntegerField(
        'Рейтинг',
        validators=[
            MaxValueValidator(
                10, message='Оценка должна быть не более 10 баллов.'
            ),
            MinValueValidator(
                1, message='Оценка должна быть не менее 1 балла.'
            ),
        ]
    )
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        auto_now_add=True,
    )

    class Meta:

        verbose_name = 'обзор'
        verbose_name_plural = 'Обзоры'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'title',
                    'author',
                ],
                name='unique_title_owner'
            )
        ]
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:MAX_LENGTH_STR]


class Comment(models.Model):
    """Модель для хранения комментариев к обзорам."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Обзор',
    )
    text = models.TextField(
        'Текст комментария',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:MAX_LENGTH_STR]
