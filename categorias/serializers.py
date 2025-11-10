from rest_framework import serializers
from .models import Categoria


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['idCategoria', 'nombre', 'descripcion', 'activo', 'fecha_creacion', 'fecha_actualizacion']
        read_only_fields = ['idCategoria', 'fecha_creacion', 'fecha_actualizacion']
