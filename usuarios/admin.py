from django.contrib import admin
from .models import Rol, Usuario


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['idRol', 'nombre', 'descripcion']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['idUsuario', 'username', 'email', 'rol', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'rol', 'fecha_creacion']
    search_fields = ['username', 'email']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    ordering = ['-fecha_creacion']
    
    fieldsets = (
        ('Información básica', {
            'fields': ('username', 'email', 'password')
        }),
        ('Rol y permisos', {
            'fields': ('rol', 'activo')
        }),
        ('Notificaciones', {
            'fields': ('fcmToken',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
