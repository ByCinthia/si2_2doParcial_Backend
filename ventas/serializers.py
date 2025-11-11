from django.db import transaction
from productos.models import Product
from rest_framework import serializers
from .models import Pedido, PedidoItem, Venta, DetalleVenta
from productos.models import ProductVariant


class PedidoItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = PedidoItem
        fields = ['idItem', 'producto', 'variante', 'nombre', 'cantidad', 'precio', 'subtotal']
    
    def get_subtotal(self, obj):
        return obj.subtotal()


class PedidoSerializer(serializers.ModelSerializer):
    items = PedidoItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Pedido
        fields = [
            'idPedido', 'cliente', 'total', 'metodo_pago', 
            'datos_cliente', 'recoger_hasta', 'estado',
            'fecha_creacion', 'fecha_actualizacion', 
            'items', 'items_count'
        ]
    
    def get_items_count(self, obj):
        return obj.items.count()


class DetalleVentaSerializer(serializers.ModelSerializer):
    """Detalle de venta CON cálculo de ganancia"""
    producto_nombre = serializers.CharField(source='producto.name', read_only=True)
    costo_unitario = serializers.SerializerMethodField()
    ganancia_unitaria = serializers.SerializerMethodField()
    ganancia_total = serializers.SerializerMethodField()
    margen_porcentaje = serializers.SerializerMethodField()
    
    class Meta:
        model = DetalleVenta
        fields = [
            'id', 'producto', 'producto_nombre',
            'cantidad', 
            'precio_unitario',  # Precio de VENTA
            'costo_unitario',   # Precio de COSTO
            'subtotal',         # Ingresos totales
            'ganancia_unitaria', 'ganancia_total', 'margen_porcentaje',
            'created_at'
        ]
    
    def get_costo_unitario(self, obj):
        """Obtiene el costo del producto al momento de la venta"""
        # Aquí deberías guardar el costo en el momento de la venta
        # Por ahora, lo obtenemos del producto actual
        return str(obj.producto.cost_price)
    
    def get_ganancia_unitaria(self, obj):
        """Ganancia por unidad = precio_venta - costo"""
        costo = obj.producto.cost_price
        return str(obj.precio_unitario - costo)
    
    def get_ganancia_total(self, obj):
        """Ganancia total = (precio_venta - costo) * cantidad"""
        costo = obj.producto.cost_price
        ganancia_unitaria = obj.precio_unitario - costo
        return str(ganancia_unitaria * obj.cantidad)
    
    def get_margen_porcentaje(self, obj):
        """Margen de ganancia en %"""
        costo = obj.producto.cost_price
        if costo > 0:
            margen = ((obj.precio_unitario - costo) / costo) * 100
            return round(float(margen), 2)
        return 0


class VentaSerializer(serializers.ModelSerializer):
    items = DetalleVentaSerializer(many=True, read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    total_ganancia = serializers.SerializerMethodField()
    total_costo = serializers.SerializerMethodField()
    margen_promedio = serializers.SerializerMethodField()
    
    class Meta:
        model = Venta
        fields = [
            'id', 'usuario', 'usuario_nombre', 'fecha',
            'total',  # Ingresos totales
            'total_costo', 'total_ganancia', 'margen_promedio',
            'items'
        ]
    
    def get_total_costo(self, obj):
        """Suma de costos de todos los items"""
        total = sum(
            item.producto.cost_price * item.cantidad 
            for item in obj.items.all()
        )
        return str(total)
    
    def get_total_ganancia(self, obj):
        """Ganancia total = ingresos - costos"""
        total_ingresos = obj.total
        total_costos = sum(
            item.producto.cost_price * item.cantidad 
            for item in obj.items.all()
        )
        return str(total_ingresos - total_costos)
    
    def get_margen_promedio(self, obj):
        """Margen promedio ponderado por ingresos"""
        total_ingresos = float(obj.total)
        total_costos = sum(
            float(item.producto.cost_price) * item.cantidad 
            for item in obj.items.all()
        )
        if total_costos > 0:
            margen = ((total_ingresos - total_costos) / total_costos) * 100
            return round(margen, 2)
        return 0


class YourSerializer(serializers.Serializer):
    # Your serializer fields here

    def create(self, validated_data):
        from django.db import transaction
        from productos.models import Product

        with transaction.atomic():
            # Your create logic here
            pid = validated_data.get('product_id')
            if pid:
                try:
                    producto_obj = Product.objects.get(pk=pid)
                except Product.DoesNotExist:
                    producto_obj = None

        # Return the created object or any other relevant data
        return producto_obj