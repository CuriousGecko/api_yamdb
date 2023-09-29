from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Предоставляет доступ только администратору."""

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'admin' or request.user.is_superuser
        return False


class OwnerOnly(permissions.BasePermission):
    """Предоставляет доступ только владельцу."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.username == request.user

      
class IsAuthorOrReadOnly(permissions.BasePermission):
    """Предоставляет доступ на редактирование только автору."""
  
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
