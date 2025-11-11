from django.contrib import admin
from .models import Proveedor, Compra, DetalleCompra


class DetalleCompraInline(admin.TabularInline):
    model = DetalleCompra
    extra = 1
    readonly_fields = ('subtotal', 'fecha_creacion')
    fields = ('producto', 'cantidad', 'precio', 'subtotal')


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('idProveedor', 'nombre', 'telefono', 'email', 'fecha_creacion')
    search_fields = ('nombre', 'email', 'telefono')
    list_filter = ('fecha_creacion',)
    ordering = ('nombre',)
    readonly_fields = ('idProveedor', 'fecha_creacion', 'fecha_modificacion')
    
    fieldsets = (
        ('Información del Proveedor', {
            'fields': ('idProveedor', 'nombre', 'telefono', 'email')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display = ('idCompra', 'proveedor', 'total', 'fecha_compra', 'tiene_comprobante')
    search_fields = ('proveedor__nombre',)
    list_filter = ('fecha_compra', 'proveedor')
    ordering = ('-fecha_compra',)
    readonly_fields = ('idCompra', 'total', 'fecha_compra', 'fecha_modificacion')
    inlines = [DetalleCompraInline]
    
    fieldsets = (
        ('Información de la Compra', {
            'fields': ('idCompra', 'proveedor', 'total', 'imagen')
        }),
        ('Fechas', {
            'fields': ('fecha_compra', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
    
    def tiene_comprobante(self, obj):
        return "✅" if obj.imagen else "❌"
    tiene_comprobante.short_description = 'Comprobante'


@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    list_display = ('idDetalleCompra', 'compra', 'producto', 'cantidad', 'precio', 'subtotal', 'fecha_creacion')
    search_fields = ('compra__idCompra', 'producto__nombre')
    list_filter = ('fecha_creacion',)
    ordering = ('-fecha_creacion',)
    readonly_fields = ('idDetalleCompra', 'subtotal', 'fecha_creacion', 'fecha_modificacion')
    
    fieldsets = (
        ('Información del Detalle', {
            'fields': ('idDetalleCompra', 'compra', 'producto', 'cantidad', 'precio', 'subtotal')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
