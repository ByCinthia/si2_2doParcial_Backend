from django.db import models
from django.conf import settings

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
    ESTADOS_VENTA = (('CREADA','Creada'), ('ANULADA','Anulada'), ('FINALIZADA','Finalizada'))
    idVenta = models.AutoField(primary_key=True)
    pedido = models.OneToOneField(Pedido, null=True, blank=True, on_delete=models.SET_NULL, related_name='venta')
    cliente = models.ForeignKey('usuarios.Usuario', null=True, blank=True, on_delete=models.SET_NULL, related_name='ventas')
    vendedor = models.ForeignKey('usuarios.Usuario', null=True, blank=True, on_delete=models.SET_NULL, related_name='ventas_realizadas')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_VENTA, default='CREADA')

    def __str__(self):
        return f"Venta {self.idVenta} - {self.fecha}"


class VentaItem(models.Model):
    idItem = models.AutoField(primary_key=True)
    venta = models.ForeignKey(Venta, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey('productos.Product', null=True, blank=True, on_delete=models.SET_NULL)
    variante = models.ForeignKey('productos.ProductVariant', null=True, blank=True, on_delete=models.SET_NULL)
    nombre = models.CharField(max_length=255)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario
