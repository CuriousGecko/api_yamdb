from django.db.models import prefetch_related_objects
from rest_framework.response import Response


class PatchModelMixin:
    """Миксин частично обновляет ресурс."""

    def perform_update(self, serializer, **kwargs):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        queryset = self.filter_queryset(self.get_queryset())
        if queryset._prefetch_related_lookups:
            instance._prefetched_objects_cashe = {}
            prefetch_related_objects(
                [instance],
                *queryset._prefetch_related_lookups,
            )
        return Response(serializer.data)
