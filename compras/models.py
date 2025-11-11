from django.db import models
from cloudinary.models import CloudinaryField


class Proveedor(models.Model):
    idProveedor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'proveedor'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
class Compra(models.Model):
    idCompra = models.AutoField(primary_key=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='compras')
    total = models.FloatField()
    fecha_compra = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    imagen = CloudinaryField('imagen', blank=True, null=True)
    
    class Meta:
        db_table = 'compra'
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'
        ordering = ['-fecha_compra']
    
    def __str__(self):
        return f'Compra {self.idCompra} - Proveedor: {self.proveedor.nombre}'
    

class DetalleCompra(models.Model):
    idDetalleCompra = models.AutoField(primary_key=True)
    
    producto = models.ForeignKey('productos.Producto', on_delete=models.PROTECT, related_name='detalles_compra')
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')

    cantidad = models.IntegerField()
    precio = models.FloatField()
    subtotal = models.FloatField()

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'detalle_compra'
        verbose_name = 'Detalle de Compra'
        verbose_name_plural = 'Detalles de Compras'
        ordering = ['idDetalleCompra']
    
    def __str__(self):
        return f'Detalle {self.idDetalleCompra} - Compra: {self.compra.idCompra}'
