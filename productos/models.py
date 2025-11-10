from django.db import models

# Create your models here.

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    # usar URLField para simplicidad; puedes cambiar a ImageField + storage si configuras cloudinary/local
    image_url = models.URLField(max_length=1000, blank=True)

    def __str__(self):
        return f"Image for {self.product_id}"

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
