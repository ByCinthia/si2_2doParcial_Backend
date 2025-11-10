from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    """
    Permiso que solo permite acceso a usuarios con rol SuperAdmin
    """
    def has_permission(self, request, view):
        return (request.user and 
                hasattr(request.user, 'rol') and 
                request.user.rol and 
                request.user.rol.nombre == 'SuperAdmin')

class CanManageUsers(BasePermission):
    """
    Permiso para gestionar usuarios (SuperAdmin, Trabajador, Vendedor)
    """
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'rol') or not request.user.rol:
            return False
        
        allowed_roles = ['SuperAdmin', 'Trabajador', 'Vendedor']
        return request.user.rol.nombre in allowed_roles

class CanCreateClients(BasePermission):
    """
    Permiso para crear clientes (SuperAdmin, Trabajador, Vendedor, Cajero)
    """
    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, 'rol') or not request.user.rol:
            return False
        
        allowed_roles = ['SuperAdmin', 'Trabajador', 'Vendedor', 'Cajero']
        return request.user.rol.nombre in allowed_roles

class CanManageRoles(BasePermission):
    """
    Permiso para gestionar roles (solo SuperAdmin)
    """
    def has_permission(self, request, view):
        return (request.user and 
                hasattr(request.user, 'rol') and 
                request.user.rol and 
                request.user.rol.nombre == 'SuperAdmin')