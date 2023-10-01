from django_filters.rest_framework import CharFilter, FilterSet

from reviews.models import Title


class FilterTitle(FilterSet):
    genre = CharFilter('genre__slug')
    category = CharFilter('category__slug')

    class Meta:
        model = Title
        fields = (
            'name',
            'year',
        )
