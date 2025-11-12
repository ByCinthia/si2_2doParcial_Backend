from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Permiso personalizado para verificar que el usuario es administrador.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.rol.nombre == 'Administrador'


class IsClienteUser(BasePermission):
    """
    Permiso personalizado para verificar que el usuario es cliente.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.rol.nombre == 'Cliente'
