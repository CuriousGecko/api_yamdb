from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Предоставляет доступ только администратору."""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'admin' or request.user.is_superuser
        return False


class OwnerOnly(permissions.BasePermission):
    """Предоставляет доступ только владельцу аккаунта."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.username == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """Полный доступ администратору и безопасные методы для остальных."""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'admin' or request.user.is_superuser
        return request.method in permissions.SAFE_METHODS


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
            or request.user == 'admin'
            or request.user == 'moderator'
            or obj.author == request.user
            or request.user.is_superuser
        )
