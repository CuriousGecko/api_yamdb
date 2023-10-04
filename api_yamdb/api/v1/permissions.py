from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Предоставляет доступ только администратору/суперпользователю."""
    # Там где используется - да, только для админа.

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin_or_superuser
        )


class OwnerOnly(permissions.BasePermission):
    """Предоставляет доступ только владельцу аккаунта."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.username == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """Полный доступ администратору и безопасные методы для остальных."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin_or_superuser
            or request.method in permissions.SAFE_METHODS
        )


class IsAdminModeratorAuthorOrReadOnly(permissions.BasePermission):
    """Доступ для админа, модератора, автора и безопасные методы для иных."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            or request.method in permissions.SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_admin_or_superuser
            or request.user.is_moderator
            or request.user == obj.author
            or request.user.is_superuser
        )
