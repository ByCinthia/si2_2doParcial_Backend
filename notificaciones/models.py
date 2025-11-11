from django.db import models


# Create your models here.

class Notificacion(models.Model):
    idNotificacion = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notificacion'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.titulo
    
class UserNoti(models.Model):
    idUserNoti = models.AutoField(primary_key=True)
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE, related_name='notificaciones_usuario')
    notificacion = models.ForeignKey(Notificacion, on_delete=models.CASCADE, related_name='usuarios_notificacion')
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_noti'
        verbose_name = 'Usuario Notificación'
        verbose_name_plural = 'Usuarios Notificaciones'
        ordering = ['-notificacion__fecha_creacion']
    
    def __str__(self):
        return f'Notificación {self.notificacion.titulo} para {self.usuario.username}'