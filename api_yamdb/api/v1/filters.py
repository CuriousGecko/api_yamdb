from django_filters.rest_framework import CharFilter, FilterSet

from reviews.models import Title


class TitleFilter(FilterSet):
    """Фильтр преобразовывает поля жанра и категории."""

    genre = CharFilter(
        field_name='genre__slug',
    )
    category = CharFilter(
        field_name='category__slug',
    )

    class Meta:
        model = Title
        fields = (
            'name',
            'year',
        )
