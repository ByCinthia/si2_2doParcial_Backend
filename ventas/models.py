from django.db import models
from django.utils import timezone

# Create your models here.

class MetodoPago(models.Model):
    idMetodoPago = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'metodo_pago'
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Venta(models.Model):
    OPCIONES_CUOTAS = [
        (1, 'Al contado'),
        (3, '3 cuotas'),
        (6, '6 cuotas'),
        (12, '12 cuotas'),
    ]
    
    idVenta = models.AutoField(primary_key=True)
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.PROTECT, related_name='ventas')
    metodoPago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT, related_name='ventas')
    
    # Montos
    subtotal = models.FloatField()  # Suma de productos
    interes = models.FloatField(default=0.0)  # Tasa de interés anual (ej: 0.15 = 15%)
    total = models.FloatField()  # subtotal + (subtotal * interes_calculado)
    
    # Cuotas
    nrocuotas = models.IntegerField(default=1, choices=OPCIONES_CUOTAS)
    
    # Stripe
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Timestamps
    fecha_venta = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'venta'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha_venta']

    def __str__(self):
        return f'Venta {self.idVenta} - Total: ${self.total}'  


class DetalleVenta(models.Model):
    idDetalleVenta = models.AutoField(primary_key=True)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey('productos.Producto', on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio = models.FloatField()  # Precio unitario al momento de la venta
    subtotal = models.FloatField()  # cantidad * precio

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'detalle_venta'
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Ventas'
        ordering = ['idDetalleVenta']

    def __str__(self):
        return f'DetalleVenta {self.idDetalleVenta} - Venta: {self.venta.idVenta}' 




class Cuota(models.Model):
    idCuota = models.AutoField(primary_key=True)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='cuotas')
    
    numero_cuota = models.IntegerField()  # 1, 2, 3...
    monto = models.FloatField()  # Monto de la cuota
    
    # Estado de pago
    pagada = models.BooleanField(default=False)
    fecha_vencimiento = models.DateField()
    fecha_pago = models.DateField(blank=True, null=True)
    
    # Stripe - Para pago dentro de Flutter
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Stripe - Para pago con link externo (Web)
    stripe_checkout_session_id = models.CharField(max_length=255, blank=True, null=True)
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cuota'
        verbose_name = 'Cuota'
        verbose_name_plural = 'Cuotas'
        ordering = ['venta', 'numero_cuota']
        unique_together = ['venta', 'numero_cuota']

    def __str__(self):
        return f'Cuota {self.numero_cuota}/{self.venta.nrocuotas} - Venta {self.venta.idVenta}'
    
    @property
    def esta_vencida(self):
        """Verifica si la cuota está vencida"""
        if self.pagada:
            return False
        return timezone.now().date() > self.fecha_vencimiento 
