from notificaciones.models import Notificacion, UserNoti
from notificaciones.serializers import (
    NotificacionSerializer, 
    UserNotiSerializer,
    UserNotiDetailSerializer
)
from usuarios.models import Usuario
from rest_framework import status
from .firebase_config import (
    send_push_notification,
    send_push_notification_multicast,
    initialize_firebase
)


class NotificacionService:
    """Servicio para manejar la lógica de negocio de Notificaciones"""
    
    @staticmethod
    def enviar_notificacion(titulo, mensaje, usuarios_ids=None, enviar_push=True):
        """
        Crea y envía una notificación a uno o varios usuarios.
        Si usuarios_ids es None, se envía a todos los usuarios.
        
        Args:
            titulo (str): Título de la notificación
            mensaje (str): Mensaje de la notificación
            usuarios_ids (list, optional): Lista de IDs de usuarios
            enviar_push (bool): Si se debe enviar notificación push
        
        Returns:
            tuple: (success: bool, data: dict, status_code: int)
        """
        try:
            # Crear la notificación
            notificacion = Notificacion.objects.create(
                titulo=titulo,
                mensaje=mensaje
            )
            
            # Obtener usuarios
            if usuarios_ids:
                usuarios = Usuario.objects.filter(idUsuario__in=usuarios_ids, activo=True)
            else:
                usuarios = Usuario.objects.filter(activo=True)
            
            if not usuarios.exists():
                return False, {"error": "No se encontraron usuarios activos"}, status.HTTP_404_NOT_FOUND
            
            # Crear UserNoti para cada usuario
            user_notis = []
            for usuario in usuarios:
                user_noti = UserNoti.objects.create(
                    usuario=usuario,
                    notificacion=notificacion,
                    leido=False
                )
                user_notis.append(user_noti)
            
            # Enviar notificación push si está habilitado
            push_result = None
            if enviar_push:
                initialize_firebase()
                fcm_tokens = [u.fcmToken for u in usuarios if u.fcmToken]
                
                if fcm_tokens:
                    success_count, failure_count, responses = send_push_notification_multicast(
                        fcm_tokens=fcm_tokens,
                        title=titulo,
                        body=mensaje,
                        data={
                            'notificacion_id': str(notificacion.idNotificacion),
                            'tipo': 'notificacion'
                        }
                    )
                    push_result = {
                        'enviados': success_count,
                        'fallidos': failure_count,
                        'total_tokens': len(fcm_tokens)
                    }
            
            return True, {
                "mensaje": "Notificación enviada correctamente",
                "notificacion_id": notificacion.idNotificacion,
                "usuarios_notificados": usuarios.count(),
                "push_enviado": push_result
            }, status.HTTP_201_CREATED
            
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def listar_notificaciones_usuario(id_usuario):
        """Lista todas las notificaciones de un usuario"""
        try:
            user_notis = UserNoti.objects.filter(
                usuario__idUsuario=id_usuario
            ).select_related('notificacion', 'usuario').order_by('-notificacion__fecha_creacion')
            
            serializer = UserNotiSerializer(user_notis, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def marcar_como_leida(id_user_noti, id_usuario):
        """Marca una notificación como leída"""
        try:
            user_noti = UserNoti.objects.get(
                idUserNoti=id_user_noti,
                usuario__idUsuario=id_usuario
            )
            user_noti.leido = True
            user_noti.save()
            
            serializer = UserNotiSerializer(user_noti)
            return True, serializer.data, status.HTTP_200_OK
        except UserNoti.DoesNotExist:
            return False, {"error": "Notificación no encontrada"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def marcar_todas_como_leidas(id_usuario):
        """Marca todas las notificaciones de un usuario como leídas"""
        try:
            count = UserNoti.objects.filter(
                usuario__idUsuario=id_usuario,
                leido=False
            ).update(leido=True)
            
            return True, {
                "mensaje": "Notificaciones marcadas como leídas",
                "cantidad": count
            }, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def contar_no_leidas(id_usuario):
        """Cuenta las notificaciones no leídas de un usuario"""
        try:
            count = UserNoti.objects.filter(
                usuario__idUsuario=id_usuario,
                leido=False
            ).count()
            
            return True, {"no_leidas": count}, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def eliminar_notificacion(id_user_noti, id_usuario):
        """Elimina una notificación de un usuario"""
        try:
            user_noti = UserNoti.objects.get(
                idUserNoti=id_user_noti,
                usuario__idUsuario=id_usuario
            )
            user_noti.delete()
            
            return True, {"mensaje": "Notificación eliminada"}, status.HTTP_200_OK
        except UserNoti.DoesNotExist:
            return False, {"error": "Notificación no encontrada"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
