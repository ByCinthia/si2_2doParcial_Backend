from django.urls import path
from .views import (
    EnviarNotificacionView,
    ListarNotificacionesUsuarioView,
    MarcarComoLeidaView,
    MarcarTodasLeidasView,
    ContarNoLeidasView,
    EliminarNotificacionView
)

urlpatterns = [
    # Enviar notificaciones (admin/staff)
    path('enviar/', EnviarNotificacionView.as_view(), name='enviar-notificacion'),
    
    # Notificaciones del usuario
    path('mis-notificaciones/', ListarNotificacionesUsuarioView.as_view(), name='mis-notificaciones'),
    path('no-leidas/', ContarNoLeidasView.as_view(), name='contar-no-leidas'),
    path('marcar-todas-leidas/', MarcarTodasLeidasView.as_view(), name='marcar-todas-leidas'),
    
    # Acciones sobre notificaciones individuales
    path('<int:id_user_noti>/marcar-leida/', MarcarComoLeidaView.as_view(), name='marcar-leida'),
    path('<int:id_user_noti>/', EliminarNotificacionView.as_view(), name='eliminar-notificacion'),
]
