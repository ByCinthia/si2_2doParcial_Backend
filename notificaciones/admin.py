from django.contrib import admin
from .models import Notificacion, UserNoti


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('idNotificacion', 'titulo', 'fecha_creacion')
    search_fields = ('titulo', 'mensaje')
    list_filter = ('fecha_creacion',)
    ordering = ('-fecha_creacion',)
    readonly_fields = ('idNotificacion', 'fecha_creacion')
    
    fieldsets = (
        ('Información de la Notificación', {
            'fields': ('idNotificacion', 'titulo', 'mensaje', 'fecha_creacion')
        }),
    )


@admin.register(UserNoti)
class UserNotiAdmin(admin.ModelAdmin):
    list_display = ('idUserNoti', 'usuario', 'get_titulo_notificacion', 'leido', 'fecha_creacion')
    search_fields = ('usuario__nombre', 'notificacion__titulo')
    list_filter = ('leido', 'fecha_creacion')
    ordering = ('-fecha_creacion',)
    readonly_fields = ('idUserNoti', 'fecha_creacion')
    
    fieldsets = (
        ('Información', {
            'fields': ('idUserNoti', 'usuario', 'notificacion', 'leido', 'fecha_creacion')
        }),
    )
    
    def get_titulo_notificacion(self, obj):
        return obj.notificacion.titulo
    get_titulo_notificacion.short_description = 'Título'
