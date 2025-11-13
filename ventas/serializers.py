from rest_framework import serializers
from django.db import transaction
from .models import MetodoPago, Pedido, PedidoItem, Venta, DetalleVenta, MovimientoInventario
from productos.models import Product, ProductVariant


class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = ['id', 'nombre', 'activo', 'requiere_comprobante', 'descripcion', 'icono']


class PedidoItemSerializer(serializers.ModelSerializer):
    """Serializer para items del pedido"""
    
    class Meta:
        model = PedidoItem
        fields = [
            'idItem', 'producto', 'variante', 
            'nombre_completo', 'sku',
            'cantidad', 'precio_unitario', 'subtotal',
            'stock_reservado'
        ]
        read_only_fields = ['idItem', 'subtotal', 'stock_reservado']


class PedidoSerializer(serializers.ModelSerializer):
    """Serializer para pedidos"""
    items = PedidoItemSerializer(many=True, read_only=True)
    metodo_pago_info = MetodoPagoSerializer(source='metodo_pago', read_only=True)
    
    class Meta:
        model = Pedido
        fields = [
            'idPedido', 'cliente', 'datos_cliente',
            'subtotal', 'descuento', 'total',
            'estado', 'metodo_pago', 'metodo_pago_info',
            'comprobante_pago', 'fecha_pago',
            'fecha_creacion', 'fecha_actualizacion', 'fecha_expiracion',
            'observaciones', 'ip_cliente',
            'items'
        ]
        read_only_fields = ['idPedido', 'fecha_creacion', 'fecha_actualizacion']


class CrearPedidoSerializer(serializers.Serializer):
    """Serializer para crear un pedido completo"""
    datos_cliente = serializers.JSONField()
    items = serializers.ListField()
    metodo_pago_id = serializers.IntegerField()
    observaciones = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_items(self, value):
        """Validar que los items tengan la estructura correcta"""
        if not value:
            raise serializers.ValidationError("Debe incluir al menos un producto")
        
        for item in value:
            # Validar campos requeridos
            required_fields = ['producto_id', 'variante_id', 'cantidad', 'precio']
            for field in required_fields:
                if field not in item:
                    raise serializers.ValidationError(f"Falta el campo '{field}' en un item")
            
            # Validar tipos
            try:
                item['cantidad'] = int(item['cantidad'])
                item['precio'] = float(item['precio'])
                if item['cantidad'] <= 0:
                    raise serializers.ValidationError("La cantidad debe ser mayor a 0")
                if item['precio'] <= 0:
                    raise serializers.ValidationError("El precio debe ser mayor a 0")
            except (ValueError, TypeError):
                raise serializers.ValidationError("Cantidad y precio deben ser números")
        
        return value
    
    def validate_metodo_pago_id(self, value):
        """Validar que el método de pago existe y está activo"""
        try:
            metodo = MetodoPago.objects.get(id=value, activo=True)
            return value
        except MetodoPago.DoesNotExist:
            raise serializers.ValidationError("Método de pago inválido o inactivo")
    
    @transaction.atomic
    def create(self, validated_data):
        """Crear pedido con items y reservar stock"""
        user = self.context['request'].user
        
        # Crear pedido
        pedido = Pedido.objects.create(
            cliente=user if user.is_authenticated else None,
            datos_cliente=validated_data['datos_cliente'],
            metodo_pago_id=validated_data['metodo_pago_id'],
            observaciones=validated_data.get('observaciones', ''),
            ip_cliente=self.context['request'].META.get('REMOTE_ADDR')
        )
        
        # Procesar items
        subtotal = 0
        for item_data in validated_data['items']:
            # Obtener producto y variante
            try:
                producto = Product.objects.get(id=item_data['producto_id'])
                variante = ProductVariant.objects.get(id=item_data['variante_id'])
            except (Product.DoesNotExist, ProductVariant.DoesNotExist):
                raise serializers.ValidationError("Producto o variante no encontrado")
            
            # Validar stock
            cantidad = item_data['cantidad']
            if variante.stock < cantidad:
                raise serializers.ValidationError(
                    f"Stock insuficiente para {producto.name} ({variante.size}). "
                    f"Disponible: {variante.stock}, Solicitado: {cantidad}"
                )
            
            # RESERVAR STOCK (reducir inmediatamente)
            variante.reduce_stock(
                quantity=cantidad, 
                pedido=pedido, 
                usuario=user if user.is_authenticated else None
            )
            
            # Crear item del pedido
            precio_unitario = item_data['precio']
            item_subtotal = cantidad * precio_unitario
            
            nombre_completo = f"{producto.name}"
            if variante.size:
                nombre_completo += f" - {variante.size}"
            if variante.color:
                nombre_completo += f" - {variante.color}"
            
            PedidoItem.objects.create(
                pedido=pedido,
                producto=producto,
                variante=variante,
                nombre_completo=nombre_completo,
                sku=variante.sku or '',
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=item_subtotal,
                stock_reservado=True
            )
            
            subtotal += item_subtotal
        
        # Actualizar totales del pedido
        pedido.subtotal = subtotal
        pedido.total = subtotal - pedido.descuento
        pedido.save()
        
        return pedido


class DetalleVentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleVenta
        fields = [
            'id', 'producto', 'variante',
            'nombre_completo', 'sku', 'categoria_nombre',
            'cantidad', 'precio_unitario', 'subtotal',
            'costo_unitario', 'costo_total',
            'ganancia_unitaria', 'ganancia_total', 'margen_porcentaje'
        ]


class VentaSerializer(serializers.ModelSerializer):
    items = DetalleVentaSerializer(many=True, read_only=True)
    metodo_pago_info = MetodoPagoSerializer(source='metodo_pago', read_only=True)
    pedido_info = PedidoSerializer(source='pedido', read_only=True)
    
    class Meta:
        model = Venta
        fields = [
            'id', 'pedido', 'pedido_info',
            'usuario_vendedor', 'cliente', 'datos_cliente',
            'subtotal', 'descuento', 'total',
            'costo_total', 'ganancia_total', 'margen_porcentaje',
            'metodo_pago', 'metodo_pago_info', 'comprobante_pago',
            'estado', 'fecha', 'fecha_anulacion', 'motivo_anulacion',
            'ip_cliente', 'items'
        ]


class ConfirmarPedidoSerializer(serializers.Serializer):
    """Confirmar pedido (crear venta)"""
    comprobante_pago = serializers.CharField(max_length=255, required=False, allow_blank=True)
    
    @transaction.atomic
    def create(self, validated_data):
        """Convertir pedido en venta"""
        pedido = self.context['pedido']
        user = self.context['request'].user
        
        if pedido.estado != 'PENDIENTE':
            raise serializers.ValidationError("El pedido ya fue procesado")
        
        # Calcular costos totales
        costo_total = 0
        for item in pedido.items.all():
            costo_unitario = item.variante.get_cost_price() if item.variante else item.producto.cost_price
            costo_total += item.cantidad * costo_unitario
        
        ganancia_total = pedido.total - costo_total
        margen_porcentaje = (ganancia_total / costo_total * 100) if costo_total > 0 else 0
        
        # Crear venta
        venta = Venta.objects.create(
            pedido=pedido,
            usuario_vendedor=user,
            cliente=pedido.cliente,
            datos_cliente=pedido.datos_cliente,
            subtotal=pedido.subtotal,
            descuento=pedido.descuento,
            total=pedido.total,
            costo_total=costo_total,
            ganancia_total=ganancia_total,
            margen_porcentaje=margen_porcentaje,
            metodo_pago=pedido.metodo_pago,
            comprobante_pago=validated_data.get('comprobante_pago', ''),
            ip_cliente=pedido.ip_cliente
        )
        
        # Crear detalles de venta
        for item in pedido.items.all():
            costo_unitario = item.variante.get_cost_price() if item.variante else item.producto.cost_price
            
            DetalleVenta.objects.create(
                venta=venta,
                producto=item.producto,
                variante=item.variante,
                nombre_completo=item.nombre_completo,
                sku=item.sku,
                categoria_nombre=item.producto.categoria.nombre if item.producto.categoria else '',
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario,
                costo_unitario=costo_unitario
            )
        
        # Actualizar estado del pedido
        pedido.estado = 'PAGADO'
        pedido.fecha_pago = timezone.now()
        pedido.comprobante_pago = validated_data.get('comprobante_pago', '')
        pedido.save()
        
        return venta


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovimientoInventario
        fields = [
            'id', 'tipo', 'variante', 'pedido', 'venta',
            'cantidad', 'stock_anterior', 'stock_nuevo',
            'usuario', 'observaciones', 'fecha'
        ]