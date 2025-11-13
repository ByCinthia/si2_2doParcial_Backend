from django.contrib import admin
from .models import Product, ProductImage, ProductVariant


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'cost_price', 'active', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['active', 'categoria']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'is_main', 'order', 'created_at']
    search_fields = ['product__name', 'alt_text']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'sku', 'size', 'color', 'stock']
    search_fields = ['product__name', 'sku']
    list_filter = ['size', 'color']
