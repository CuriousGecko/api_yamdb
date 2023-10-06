from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Предоставляет доступ админу/суперпользователю."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class OwnerOnly(permissions.BasePermission):
    """Предоставляет доступ только владельцу аккаунта."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.username == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """Предоставляет доступ админу и безопасные методы."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
            or request.method in permissions.SAFE_METHODS
        )


class IsAdminModeratorAuthorOrReadOnly(permissions.BasePermission):
    """Предоставляет доступ админу, модератору, автору и безопасные методы."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            or request.method in permissions.SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin
            or request.user.is_moderator
            or request.user == obj.author
            or request.user.is_superuser
        )
