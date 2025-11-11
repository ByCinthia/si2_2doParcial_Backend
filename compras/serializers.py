from rest_framework import serializers
from compras.models import Proveedor, Compra, DetalleCompra
from productos.serializers import ProductoSerializer


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['idProveedor', 'nombre', 'telefono', 'email', 'fecha_creacion', 'fecha_modificacion']
        read_only_fields = ['idProveedor', 'fecha_creacion', 'fecha_modificacion']


class DetalleCompraSerializer(serializers.ModelSerializer):
    producto_detalle = ProductoSerializer(source='producto', read_only=True)
    nombre_producto = serializers.CharField(source='producto.nombre', read_only=True)
    
    class Meta:
        model = DetalleCompra
        fields = [
            'idDetalleCompra', 
            'producto', 
            'producto_detalle',
            'nombre_producto',
            'cantidad', 
            'precio', 
            'subtotal',
            'fecha_creacion'
        ]
        read_only_fields = ['idDetalleCompra', 'subtotal', 'fecha_creacion']


class DetalleCompraCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear detalles de compra sin el campo compra"""
    class Meta:
        model = DetalleCompra
        fields = ['producto', 'cantidad', 'precio']
    
    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0")
        return value
    
    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0")
        return value


class CompraSerializer(serializers.ModelSerializer):
    proveedor_detalle = ProveedorSerializer(source='proveedor', read_only=True)
    nombre_proveedor = serializers.CharField(source='proveedor.nombre', read_only=True)
    detalles = DetalleCompraSerializer(many=True, read_only=True)
    cantidad_productos = serializers.SerializerMethodField()
    
    class Meta:
        model = Compra
        fields = [
            'idCompra',
            'proveedor',
            'proveedor_detalle',
            'nombre_proveedor',
            'total',
            'imagen',
            'fecha_compra',
            'fecha_modificacion',
            'detalles',
            'cantidad_productos'
        ]
        read_only_fields = ['idCompra', 'total', 'fecha_compra', 'fecha_modificacion']
    
    def get_cantidad_productos(self, obj):
        return obj.detalles.count()


class CrearCompraSerializer(serializers.Serializer):
    """Serializer para crear una compra completa con sus detalles"""
    proveedor = serializers.IntegerField()
    detalles = DetalleCompraCreateSerializer(many=True)
    imagen = serializers.ImageField(required=False, allow_null=True)
    
    def validate_proveedor(self, value):
        try:
            Proveedor.objects.get(idProveedor=value)
        except Proveedor.DoesNotExist:
            raise serializers.ValidationError("El proveedor no existe")
        return value
    
    def validate_detalles(self, value):
        if not value:
            raise serializers.ValidationError("Debe incluir al menos un detalle de compra")
        return value


class ActualizarImagenCompraSerializer(serializers.Serializer):
    """Serializer para actualizar solo la imagen de una compra"""
    imagen = serializers.ImageField()
