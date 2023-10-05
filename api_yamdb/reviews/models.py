from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.validators import validate_year

STR_LIMIT = 10

User = get_user_model()


class Category(models.Model):
    """Модель для хранения категорий."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name[:STR_LIMIT]


class Genre(models.Model):
    """Модель для хранения жанров."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name[:STR_LIMIT]


class Title(models.Model):
    """
    Модель для хранения записей.
    Связь с Category через поле titles.
    Связь с Genre через поле titles_of genre
    промежуточной таблицы GenreTitle.
    """

    name = models.CharField(max_length=256)
    year = models.IntegerField(validators=[validate_year])
    description = models.TextField(max_length=256, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        blank=True,
        null=True,
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='titles_of_genre',
    )

    def __str__(self):
        return self.name[:STR_LIMIT]


class GenreTitle(models.Model):
    """Промежуточная таблица для связи Genre и Title."""

    genre = models.ForeignKey(
        Genre, on_delete=models.SET_NULL, blank=True, null=True)
    title = models.ForeignKey(
        Title, on_delete=models.SET_NULL, blank=True, null=True)

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
            MaxValueValidator(
                10, message='Оценка должна быть не более 10 баллов.'
            ),
            MinValueValidator(
                1, message='Оценка должна быть не менее 1 балла.'
            ),
        ]
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Ограничение уникальности для соблюдения правила
        "один пользователь - одна заметка к записи".
        """

        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_title_owner',
            )
        ]
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:STR_LIMIT]


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
    text = models.TextField(
        'Текст комментария',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.text[:STR_LIMIT]
