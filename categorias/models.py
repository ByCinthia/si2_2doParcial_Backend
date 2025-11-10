from django.db import models


class Categoria(models.Model):
    idCategoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categoria'
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.nombre
