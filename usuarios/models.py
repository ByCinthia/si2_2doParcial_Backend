from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Rol(models.Model):
    idRol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'rol'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    idUsuario = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    fcmToken = models.CharField(max_length=255, blank=True, null=True)
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, related_name='usuarios')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.username
    
    def set_password(self, raw_password):
        """Encripta y guarda la contraseña"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Verifica si la contraseña es correcta"""
        return check_password(raw_password, self.password)
    
    # Propiedades requeridas por Django REST Framework
    @property
    def is_authenticated(self):
        """Siempre retorna True para usuarios activos"""
        return self.activo
    
    @property
    def is_anonymous(self):
        """Siempre retorna False"""
        return False
