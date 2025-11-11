from django.db import models
from cloudinary.models import CloudinaryField
from django.utils import timezone

# Create your models here.

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    # Relacion con Categoria (protegida) - requiere que la categoría exista
    categoria = models.ForeignKey('categorias.Categoria', related_name='productos', on_delete=models.PROTECT, null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Product', related_name='images', on_delete=models.CASCADE)
    # permitir NULL/blank para no obligar un valor en filas existentes
    image = CloudinaryField('image', folder='products', blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)
    # usar default en lugar de auto_now_add para evitar conflicto con filas existentes
    # default=timezone.now dará la fecha actual en filas antiguas y nuevas
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"Image {self.id} for {self.product}"

class ProductVariant(models.Model):
    """
    Variante que representa talla/color/modelo y stock.
    price: opcional, si la variante tiene precio distinto al base_price del producto.
    """
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    sku = models.CharField(max_length=100, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    model_name = models.CharField(max_length=150, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.IntegerField(default=0)

    class Meta:
        unique_together = (('product', 'sku'),)

    def __str__(self):
        return f"{self.product.name} - {self.sku or self.id}"


class InventoryMovement(models.Model):
    """Registro de movimientos de inventario para auditoría"""
    id = models.AutoField(primary_key=True)
    variant = models.ForeignKey(ProductVariant, related_name='movimientos', on_delete=models.CASCADE)
    usuario = models.ForeignKey('usuarios.Usuario', null=True, blank=True, on_delete=models.SET_NULL)
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    delta = models.IntegerField()
    motivo = models.CharField(max_length=255, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inventory_movement'
        ordering = ['-fecha']

    def __str__(self):
        return f"Movimiento variante {self.variant_id}: {self.previous_stock} -> {self.new_stock} ({self.delta})"
