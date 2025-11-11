from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from notificaciones.services import NotificacionService
from notificaciones.serializers import EnviarNotificacionSerializer


class EnviarNotificacionView(APIView):
    """
    POST /api/notificaciones/enviar/
    Envía una notificación a uno o varios usuarios
    Requiere autenticación (admin/personal autorizado)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = EnviarNotificacionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        data = serializer.validated_data
        success, result, status_code = NotificacionService.enviar_notificacion(
            titulo=data['titulo'],
            mensaje=data['mensaje'],
            usuarios_ids=data.get('usuarios_ids'),
            enviar_push=data.get('enviar_push', True)
        )
        
        return Response(result, status=status_code)


class ListarNotificacionesUsuarioView(APIView):
    """
    GET /api/notificaciones/mis-notificaciones/
    Lista todas las notificaciones del usuario autenticado
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        id_usuario = request.user.idUsuario
        success, result, status_code = NotificacionService.listar_notificaciones_usuario(id_usuario)
        return Response(result, status=status_code)


class MarcarComoLeidaView(APIView):
    """
    PUT /api/notificaciones/{id}/marcar-leida/
    Marca una notificación específica como leída
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request, id_user_noti):
        id_usuario = request.user.idUsuario
        success, result, status_code = NotificacionService.marcar_como_leida(id_user_noti, id_usuario)
        return Response(result, status=status_code)


class MarcarTodasLeidasView(APIView):
    """
    PUT /api/notificaciones/marcar-todas-leidas/
    Marca todas las notificaciones del usuario como leídas
    """
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        id_usuario = request.user.idUsuario
        success, result, status_code = NotificacionService.marcar_todas_como_leidas(id_usuario)
        return Response(result, status=status_code)


class ContarNoLeidasView(APIView):
    """
    GET /api/notificaciones/no-leidas/
    Cuenta las notificaciones no leídas del usuario
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        id_usuario = request.user.idUsuario
        success, result, status_code = NotificacionService.contar_no_leidas(id_usuario)
        return Response(result, status=status_code)


class EliminarNotificacionView(APIView):
    """
    DELETE /api/notificaciones/{id}/
    Elimina una notificación del usuario
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, id_user_noti):
        id_usuario = request.user.idUsuario
        success, result, status_code = NotificacionService.eliminar_notificacion(id_user_noti, id_usuario)
        return Response(result, status=status_code)
