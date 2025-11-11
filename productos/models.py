from django.db import models
from cloudinary.models import CloudinaryField
from django.utils import timezone

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Precio de COSTO del producto (lo que te cuesta adquirirlo)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Precio de VENTA base (precio al público)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Relación con Categoria (opcional)
    categoria = models.ForeignKey('categorias.Categoria', related_name='productos', on_delete=models.PROTECT, null=True, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_stock(self):
        """Calcula el stock total de todas las variantes"""
        return sum(v.stock for v in self.variants.all())
    
    @property
    def is_available(self):
        """Verifica si al menos una variante tiene stock"""
        return self.total_stock > 0 and self.active
    
    @property
    def available_variants(self):
        """Retorna solo las variantes con stock disponible"""
        return self.variants.filter(stock__gt=0)
    
    @property
    def profit_margin(self):
        """Calcula el margen de ganancia (%)"""
        if self.cost_price > 0:
            return ((self.price - self.cost_price) / self.cost_price) * 100
        return 0
    
    def __str__(self):
        status = "Disponible" if self.is_available else "No disponible"
        return f"{self.name} ({status}, Stock total: {self.total_stock})"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = CloudinaryField('image', folder='products', blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Imagen de Producto'
        verbose_name_plural = 'Imágenes de Productos'

    @property
    def image_url(self):
        """Retorna la URL de Cloudinary"""
        if self.image:
            return self.image.url
        return None

    def __str__(self):
        return f"Imagen de {self.product.name} (Main: {self.is_main})"


class ProductVariant(models.Model):
    """
    Variante que representa talla/color/modelo con stock propio.
    - Cada variante puede tener precio de VENTA diferente (opcional)
    - Cada variante puede tener precio de COSTO diferente (opcional)
    - Si no se especifica, hereda los precios del producto padre
    """
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    # SKU opcional (se puede generar automáticamente o dejarlo NULL)
    sku = models.CharField(max_length=100, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    model_name = models.CharField(max_length=150, blank=True, null=True)
    
    # Precio de VENTA específico de esta variante (sobrescribe product.price si existe)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, 
                                help_text="Precio de venta al público. Si está vacío, usa el precio del producto.")
    
    # Precio de COSTO específico de esta variante (sobrescribe product.cost_price si existe)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                               help_text="Costo de adquisición. Si está vacío, usa el costo del producto.")
    
    # STOCK de esta variante específica
    stock = models.PositiveIntegerField(default=0)
    
    class Meta:
        # Permitir SKU duplicado o NULL
        db_table = 'product_variant'
        indexes = [
            models.Index(fields=['product', 'size', 'color']),
        ]

    def get_sale_price(self):
        """Retorna el precio de venta (usa el de la variante o el del producto)"""
        return self.price if self.price is not None else self.product.price
    
    def get_cost_price(self):
        """Retorna el precio de costo (usa el de la variante o el del producto)"""
        return self.cost if self.cost is not None else self.product.cost_price
    
    def get_profit(self):
        """Calcula la ganancia por unidad"""
        return self.get_sale_price() - self.get_cost_price()
    
    def get_profit_margin(self):
        """Calcula el margen de ganancia (%)"""
        cost = self.get_cost_price()
        if cost > 0:
            return ((self.get_sale_price() - cost) / cost) * 100
        return 0

    @property
    def is_available(self):
        """Verifica si la variante está disponible (stock > 0)"""
        return self.stock > 0
    
    @property
    def is_low_stock(self):
        """Verifica si el stock es bajo (< 5)"""
        return 0 < self.stock < 5
    
    def reduce_stock(self, cantidad):
        """Reduce el stock de la variante"""
        if cantidad > self.stock:
            raise ValueError(f"Stock insuficiente. Disponible: {self.stock}, Solicitado: {cantidad}")
        self.stock -= cantidad
        self.save()
        return self.stock
    
    def increase_stock(self, cantidad):
        """Incrementa el stock de la variante"""
        self.stock += cantidad
        self.save()
        return self.stock

    def __str__(self):
        parts = [self.product.name]
        if self.size:
            parts.append(f"Talla {self.size}")
        if self.color:
            parts.append(f"Color {self.color}")
        status = f"Stock: {self.stock}"
        return f"{' - '.join(parts)} ({status})"


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
