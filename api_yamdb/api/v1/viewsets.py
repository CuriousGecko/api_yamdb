from rest_framework import filters, mixins, viewsets

from api.v1.mixins import PatchModelMixin


class ListCreateDestroyViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """Базовый класс фильтрует выдачу у наследников."""

    filter_backends = (
        filters.SearchFilter,
    )
    search_fields = (
        'name',
    )


class ListCreateRetrievePatchDestroyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    PatchModelMixin,
    viewsets.GenericViewSet,
):
    pass
