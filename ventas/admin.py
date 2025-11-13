from django.contrib import admin
from .models import MetodoPago, Pedido, PedidoItem, Venta, DetalleVenta, MovimientoInventario

@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo', 'variante', 'cantidad', 'stock_anterior', 'stock_nuevo', 'fecha']
    list_filter = ['tipo', 'fecha']
    search_fields = ['variante__sku', 'variante__product__name']
