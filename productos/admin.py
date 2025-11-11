from django.contrib import admin
from .models import Product, ProductImage, ProductVariant, InventoryMovement


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ("id", "name", "base_price", "active", "created_at")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "image", "is_main", "created_at")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "sku", "price", "stock")


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ("id", "variant", "usuario", "previous_stock", "new_stock", "delta", "fecha")
