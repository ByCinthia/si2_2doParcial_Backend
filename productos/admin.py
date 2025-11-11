from django.contrib import admin
from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """Configuración del admin para Categoria"""
    list_display = ['idCategoria', 'nombre', 'descripcion', 'fecha_creacion', 'fecha_modificacion']
    search_fields = ['nombre', 'descripcion']
    list_filter = ['fecha_creacion']
    ordering = ['nombre']
    readonly_fields = ['idCategoria', 'fecha_creacion', 'fecha_modificacion']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Configuración del admin para Producto"""
    list_display = ['idProducto', 'nombre', 'precio', 'stock', 'categoria', 'fecha_creacion']
    search_fields = ['nombre']
    list_filter = ['categoria', 'fecha_creacion']
    ordering = ['-fecha_creacion']
    readonly_fields = ['idProducto', 'fecha_creacion', 'fecha_modificacion']
    list_select_related = ['categoria']

