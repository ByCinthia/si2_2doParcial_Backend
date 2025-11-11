from rest_framework import serializers
from .models import Categoria, Producto


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Categoria"""
    
    class Meta:
        model = Categoria
        fields = ['idCategoria', 'nombre', 'descripcion', 'fecha_creacion', 'fecha_modificacion']
        read_only_fields = ['idCategoria', 'fecha_creacion', 'fecha_modificacion']


class ProductoSerializer(serializers.ModelSerializer):
    """Serializer básico para Producto (para crear/actualizar)"""
    idCategoria = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Producto
        fields = ['idProducto', 'nombre', 'precio', 'stock', 'imagen', 'idCategoria', 'fecha_creacion', 'fecha_modificacion']
        read_only_fields = ['idProducto', 'fecha_creacion', 'fecha_modificacion']
    
    def create(self, validated_data):
        """Crea un producto mapeando idCategoria a categoria"""
        id_categoria = validated_data.pop('idCategoria')
        try:
            categoria = Categoria.objects.get(idCategoria=id_categoria)
            validated_data['categoria'] = categoria
            return Producto.objects.create(**validated_data)
        except Categoria.DoesNotExist:
            raise serializers.ValidationError({"idCategoria": "La categoría no existe"})
    
    def update(self, instance, validated_data):
        """Actualiza un producto mapeando idCategoria a categoria si se proporciona"""
        id_categoria = validated_data.pop('idCategoria', None)
        
        if id_categoria is not None:
            try:
                categoria = Categoria.objects.get(idCategoria=id_categoria)
                validated_data['categoria'] = categoria
            except Categoria.DoesNotExist:
                raise serializers.ValidationError({"idCategoria": "La categoría no existe"})
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ProductoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para Producto (para listar/obtener con categoría completa)"""
    categoria = CategoriaSerializer(read_only=True)
    imagen_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = ['idProducto', 'nombre', 'precio', 'stock', 'imagen', 'imagen_url', 'categoria', 'fecha_creacion', 'fecha_modificacion']
        read_only_fields = ['idProducto', 'fecha_creacion', 'fecha_modificacion']
    
    def get_imagen_url(self, obj):
        """Retorna la URL completa de la imagen de Cloudinary"""
        if obj.imagen:
            return obj.imagen.url
        return None
