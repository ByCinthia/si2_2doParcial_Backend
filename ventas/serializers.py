from rest_framework import serializers
from .models import MetodoPago, Venta, DetalleVenta, Cuota
from productos.serializers import ProductoSerializer


class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = ['idMetodoPago', 'nombre', 'descripcion', 'fecha_creacion', 'fecha_modificacion']
        read_only_fields = ['idMetodoPago', 'fecha_creacion', 'fecha_modificacion']


class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_detalle = ProductoSerializer(source='producto', read_only=True)
    nombre_producto = serializers.CharField(source='producto.nombre', read_only=True)
    
    class Meta:
        model = DetalleVenta
        fields = [
            'idDetalleVenta',
            'producto',
            'producto_detalle',
            'nombre_producto',
            'cantidad',
            'precio',
            'subtotal',
            'fecha_creacion'
        ]
        read_only_fields = ['idDetalleVenta', 'subtotal', 'fecha_creacion']


class DetalleVentaCreateSerializer(serializers.Serializer):
    """Serializer para crear detalles de venta"""
    producto = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1)
    
    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0")
        return value


class CuotaSerializer(serializers.ModelSerializer):
    esta_vencida = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Cuota
        fields = [
            'idCuota',
            'numero_cuota',
            'monto',
            'pagada',
            'fecha_vencimiento',
            'fecha_pago',
            'esta_vencida',
            'stripe_payment_intent_id',
            'stripe_checkout_session_id',
            'fecha_creacion'
        ]
        read_only_fields = ['idCuota', 'fecha_creacion']


class VentaSerializer(serializers.ModelSerializer):
    detalles = DetalleVentaSerializer(many=True, read_only=True)
    cuotas = CuotaSerializer(many=True, read_only=True)
    nombre_metodo_pago = serializers.CharField(source='metodoPago.nombre', read_only=True)
    cantidad_productos = serializers.SerializerMethodField()
    
    class Meta:
        model = Venta
        fields = [
            'idVenta',
            'usuario',
            'metodoPago',
            'nombre_metodo_pago',
            'subtotal',
            'interes',
            'total',
            'nrocuotas',
            'stripe_payment_intent_id',
            'stripe_checkout_session_id',
            'fecha_venta',
            'fecha_modificacion',
            'detalles',
            'cuotas',
            'cantidad_productos'
        ]
        read_only_fields = ['idVenta', 'subtotal', 'total', 'fecha_venta', 'fecha_modificacion']
    
    def get_cantidad_productos(self, obj):
        return obj.detalles.count()


class CrearVentaSerializer(serializers.Serializer):
    """Serializer para crear una venta completa"""
    metodoPago = serializers.IntegerField()
    nrocuotas = serializers.ChoiceField(choices=[1, 3, 6, 12])
    detalles = DetalleVentaCreateSerializer(many=True)
    
    def validate_metodoPago(self, value):
        try:
            MetodoPago.objects.get(idMetodoPago=value)
        except MetodoPago.DoesNotExist:
            raise serializers.ValidationError("El método de pago no existe")
        return value
    
    def validate_detalles(self, value):
        if not value:
            raise serializers.ValidationError("Debe incluir al menos un producto")
        return value
    
    def validate_nrocuotas(self, value):
        if value not in [1, 3, 6, 12]:
            raise serializers.ValidationError("Solo se permiten 1, 3, 6 o 12 cuotas")
        return value
