from rest_framework import serializers
from .models import Notificacion, UserNoti
from usuarios.serializers import UsuarioDetailSerializer


class NotificacionSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Notificacion"""
    
    class Meta:
        model = Notificacion
        fields = ['idNotificacion', 'titulo', 'mensaje', 'fecha_creacion']
        read_only_fields = ['idNotificacion', 'fecha_creacion']


class UserNotiSerializer(serializers.ModelSerializer):
    """Serializer para UserNoti con información de notificación"""
    notificacion = NotificacionSerializer(read_only=True)
    
    class Meta:
        model = UserNoti
        fields = ['idUserNoti', 'notificacion', 'leido', 'fecha_creacion']
        read_only_fields = ['idUserNoti', 'fecha_creacion']


class UserNotiDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para UserNoti con usuario y notificación"""
    usuario = UsuarioDetailSerializer(read_only=True)
    notificacion = NotificacionSerializer(read_only=True)
    
    class Meta:
        model = UserNoti
        fields = ['idUserNoti', 'usuario', 'notificacion', 'leido', 'fecha_creacion']
        read_only_fields = ['idUserNoti', 'fecha_creacion']


class EnviarNotificacionSerializer(serializers.Serializer):
    """Serializer para enviar notificaciones"""
    titulo = serializers.CharField(max_length=200)
    mensaje = serializers.CharField()
    usuarios = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Lista de IDs de usuarios. Si no se proporciona, se envía a todos."
    )
    enviar_push = serializers.BooleanField(default=True, required=False)
