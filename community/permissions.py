from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Права доступа для редактирования только его автором.
    """
    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.user == request.user


class IsModeratorOrAdmin(permissions.BasePermission):
    """
    Права доступа для редактирования только для модераторов или администраторов.
    """
    def has_object_permission(self, request, view, obj):
        # Разрешаем GET, HEAD и OPTIONS методы без ограничений
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Разрешаем доступ только модераторам или администраторам
        return request.user.role in ['moderator', 'admin']
