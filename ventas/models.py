from django.db import models
from django.conf import settings
from django.utils import timezone

class Pedido(models.Model):
    METODOS_PAGO = (('tarjeta','Tarjeta'), ('efectivo','Efectivo'), ('recoger','Recoger'))
    ESTADOS = (('CREADO','Creado'), ('PAGADO','Pagado'), ('CANCELADO','Cancelado'), ('COMPLETADO','Completado'))

    idPedido = models.AutoField(primary_key=True)
    cliente = models.ForeignKey('usuarios.Usuario', null=True, blank=True, on_delete=models.SET_NULL, related_name='pedidos')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO)
    datos_cliente = models.JSONField(null=True, blank=True)
    recoger_hasta = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='CREADO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido {self.idPedido} ({self.estado})"


class PedidoItem(models.Model):
    idItem = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    # referencia a producto y a variante opcional (ajusta nombres según tu app productos)
    producto = models.ForeignKey('productos.Product', null=True, blank=True, on_delete=models.SET_NULL)
    variante = models.ForeignKey('productos.ProductVariant', null=True, blank=True, on_delete=models.SET_NULL)
    nombre = models.CharField(max_length=255)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=12, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio

    def __str__(self):
        return f"{self.nombre} x{self.cantidad}"


class Venta(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ventas')
    fecha = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = 'ventas_venta'
        ordering = ['-fecha']

    def __str__(self):
        return f'Venta {self.id} - {self.usuario} - {self.total}'

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey('productos.Product', on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)  # precio de venta por unidad
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)  # cantidad * precio_unitario
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ventas_detalleventa'

    def save(self, *args, **kwargs):
        # calcular subtotal a partir de cantidad y precio_unitario siempre
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Item {self.id} - Venta {self.venta_id} - Prod {self.producto_id}'
