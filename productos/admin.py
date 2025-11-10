from django.contrib import admin
from .models import Product, ProductVariant, ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'base_price', 'categoria', 'active', 'created_at')
	search_fields = ('name',)
	list_filter = ('active', 'categoria')


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
	list_display = ('id', 'product', 'sku', 'price', 'stock')
	search_fields = ('sku',)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
	list_display = ('id', 'product', 'image_url')
