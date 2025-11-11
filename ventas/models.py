from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class MetodoPago(models.Model):
    """Catálogo de métodos de pago disponibles"""
    nombre = models.CharField(max_length=50, unique=True)  # "Efectivo", "Tarjeta Visa", "QR Bancario", etc.
    activo = models.BooleanField(default=True)
    requiere_comprobante = models.BooleanField(default=False)  # Si necesita número de transacción
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=50, blank=True)  # "cash", "credit-card", "qr", etc.
    
    class Meta:
        db_table = 'metodo_pago'
        verbose_name_plural = 'Métodos de Pago'
    
    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    """Pedido del cliente - ANTES del pago"""
    ESTADOS = (
        ('PENDIENTE', 'Pendiente de pago'),
        ('PAGADO', 'Pagado'),
        ('CANCELADO', 'Cancelado'),
        ('EXPIRADO', 'Expirado'),
    )

    idPedido = models.AutoField(primary_key=True)
    
    # Cliente (puede ser usuario registrado o invitado)
    cliente = models.ForeignKey(
        'usuarios.Usuario', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='pedidos'
    )
    
    # SNAPSHOT de datos del cliente (para auditoría)
    datos_cliente = models.JSONField(
        help_text="Nombre, email, teléfono, dirección al momento del pedido"
    )
    
    # Totales
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Estado y método de pago
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    metodo_pago = models.ForeignKey(
        MetodoPago,
        on_delete=models.PROTECT,
        related_name='pedidos',
        null=True,
        blank=True
    )
    
    # Datos de pago (cuando se confirma)
    comprobante_pago = models.CharField(max_length=255, blank=True)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_expiracion = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Pedido expira si no se paga (ej: 30 minutos)"
    )
    
    # Observaciones
    observaciones = models.TextField(blank=True)
    
    # IP del cliente (auditoría)
    ip_cliente = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'pedido'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['estado', 'fecha_creacion']),
            models.Index(fields=['cliente', 'fecha_creacion']),
        ]

    def __str__(self):
        return f"Pedido #{self.idPedido} - {self.estado}"
    
    def calcular_totales(self):
        """Calcula subtotal y total"""
        self.subtotal = sum(item.subtotal for item in self.items.all())
        self.total = self.subtotal - self.descuento
        return self.total
    
    def puede_cancelarse(self):
        """Verifica si el pedido puede cancelarse"""
        return self.estado in ['PENDIENTE', 'EXPIRADO']
    
    def esta_expirado(self):
        """Verifica si el pedido expiró"""
        if self.fecha_expiracion and self.estado == 'PENDIENTE':
            return timezone.now() > self.fecha_expiracion
        return False


class PedidoItem(models.Model):
    """Items del pedido - con SNAPSHOT de datos"""
    idItem = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    
    # Referencias a producto y variante
    producto = models.ForeignKey(
        'productos.Product', 
        on_delete=models.PROTECT,
        help_text="Producto base"
    )
    variante = models.ForeignKey(
        'productos.ProductVariant',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Variante específica (talla/color)"
    )
    
    # SNAPSHOT de datos (por si cambian después)
    nombre_completo = models.CharField(max_length=255, default='')  # "Remera Azul - M - Azul"
    sku = models.CharField(max_length=100, blank=True)
    
    # Cantidades y precios
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # CRÍTICO: Guardar stock reservado (para liberar si se cancela)
    stock_reservado = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'pedido_item'

    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre_completo} x{self.cantidad}"


class Venta(models.Model):
    """Venta confirmada - DESPUÉS del pago"""
    ESTADOS = (
        ('COMPLETADA', 'Completada'),
        ('ANULADA', 'Anulada'),
    )
    
    id = models.AutoField(primary_key=True)
    
    # Relación con pedido (trazabilidad)
    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.PROTECT,
        related_name='venta',
        help_text="Pedido origen de esta venta"
    )
    
    # Usuario que procesó la venta (vendedor)
    usuario_vendedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='ventas_procesadas'
    )
    
    # Cliente (puede ser NULL si fue invitado)
    cliente = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='compras'
    )
    
    # SNAPSHOT de datos del cliente (auditoría)
    datos_cliente = models.JSONField()
    
    # Totales
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    
    # CRÍTICO PARA REPORTES: Totales de costo y ganancia
    costo_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Suma de costos de todos los productos (snapshot)",
        default=Decimal('0.00')  # <-- agregado
    )
    ganancia_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="total - costo_total",
        default=Decimal('0.00')  # <-- agregado
    )
    margen_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="(ganancia / costo) * 100",
        default=Decimal('0.00')  # <-- agregado
    )
    
    # Método de pago usado
    metodo_pago = models.ForeignKey(
        MetodoPago,
        on_delete=models.PROTECT,
        related_name='ventas'
    )
    comprobante_pago = models.CharField(max_length=255, blank=True)
    
    # Estado
    estado = models.CharField(max_length=20, choices=ESTADOS, default='COMPLETADA')
    
    # Timestamps
    fecha = models.DateTimeField(default=timezone.now)
    fecha_anulacion = models.DateTimeField(null=True, blank=True)
    motivo_anulacion = models.TextField(blank=True)
    
    # Auditoría
    ip_cliente = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'venta'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['fecha', 'estado']),
            models.Index(fields=['usuario_vendedor', 'fecha']),
            models.Index(fields=['cliente', 'fecha']),
        ]

    def __str__(self):
        return f'Venta #{self.id} - {self.fecha.strftime("%Y-%m-%d")} - Bs. {self.total}'


class DetalleVenta(models.Model):
    """Detalle de venta - con SNAPSHOT de costos y precios"""
    id = models.AutoField(primary_key=True)
    venta = models.ForeignKey(Venta, related_name='items', on_delete=models.CASCADE)
    
    # Referencias
    producto = models.ForeignKey('productos.Product', on_delete=models.PROTECT)
    variante = models.ForeignKey(
        'productos.ProductVariant',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    
    # SNAPSHOT de datos del producto
    nombre_completo = models.CharField(max_length=255, default='')
    sku = models.CharField(max_length=100, blank=True)
    categoria_nombre = models.CharField(max_length=100, blank=True)
    
    # Cantidades y precios (SNAPSHOT al momento de venta)
    cantidad = models.PositiveIntegerField()
    
    # PRECIOS DE VENTA
    precio_unitario = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Precio de VENTA unitario"
    )
    subtotal = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="cantidad * precio_unitario"
    )
    
    # PRECIOS DE COSTO (CRÍTICO PARA REPORTES)
    costo_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Precio de COSTO unitario (snapshot)",
        default=Decimal('0.00')  # <-- agregado
    )
    costo_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="cantidad * costo_unitario",
        default=Decimal('0.00')  # <-- agregado
    )

    # GANANCIA (calculada automáticamente)
    ganancia_unitaria = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="precio_unitario - costo_unitario",
        default=Decimal('0.00')  # <-- agregado
    )
    ganancia_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="subtotal - costo_total",
        default=Decimal('0.00')  # <-- agregado
    )
    margen_porcentaje = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="(ganancia_unitaria / costo_unitario) * 100",
        default=Decimal('0.00')  # <-- agregado
    )
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'detalle_venta'

    def save(self, *args, **kwargs):
        """Calcular automáticamente todos los totales"""
        # Subtotales
        self.subtotal = self.cantidad * self.precio_unitario
        self.costo_total = self.cantidad * self.costo_unitario
        
        # Ganancias
        self.ganancia_unitaria = self.precio_unitario - self.costo_unitario
        self.ganancia_total = self.subtotal - self.costo_total
        
        # Margen
        if self.costo_unitario > 0:
            self.margen_porcentaje = (self.ganancia_unitaria / self.costo_unitario) * 100
        else:
            self.margen_porcentaje = Decimal('0')
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.nombre_completo} x{self.cantidad}'


class MovimientoInventario(models.Model):
    """Auditoría de movimientos de inventario"""
    TIPOS = (
        ('RESERVA', 'Reserva (pedido creado)'),
        ('VENTA', 'Venta (pedido confirmado)'),
        ('CANCELACION', 'Cancelación (liberar stock)'),
        ('DEVOLUCION', 'Devolución'),
        ('AJUSTE', 'Ajuste manual'),
    )
    
    id = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    
    # Relaciones
    variante = models.ForeignKey(
        'productos.ProductVariant',
        on_delete=models.CASCADE,
        related_name='movimientos'
    )
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    venta = models.ForeignKey(
        Venta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Datos del movimiento
    cantidad = models.IntegerField()  # Puede ser negativo
    stock_anterior = models.IntegerField()
    stock_nuevo = models.IntegerField()
    
    # Usuario responsable
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Observaciones
    observaciones = models.TextField(blank=True)
    
    # Timestamp
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'movimiento_inventario'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['variante', 'fecha']),
            models.Index(fields=['tipo', 'fecha']),
        ]
    
    def __str__(self):
        signo = '+' if self.cantidad > 0 else ''
        return f'{self.get_tipo_display()}: {signo}{self.cantidad} ({self.variante})'
