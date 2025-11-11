from django.urls import path
from .views import (
    CatalogoProductosListView,
    CatalogoProductoDetailView,
    CatalogoCategoriasListView,
    CatalogoProductosDestacadosView,
    CatalogoProductosNuevosView,
    CatalogoProductosMasVendidosView,
)

app_name = 'catalogo'

urlpatterns = [
    # ==================== RUTAS DE CATÁLOGO ====================
    # GET /api/catalogo/productos/ - Listar todos los productos
    # GET /api/catalogo/productos/?categoria={id} - Filtrar por categoría
    path('productos/', CatalogoProductosListView.as_view(), name='productos-list'),
    
    # GET /api/catalogo/productos/{id}/ - Obtener detalles de un producto
    path('productos/<int:id_producto>/', CatalogoProductoDetailView.as_view(), name='producto-detail'),
    
    # GET /api/catalogo/categorias/ - Listar todas las categorías
    path('categorias/', CatalogoCategoriasListView.as_view(), name='categorias-list'),
    
    # GET /api/catalogo/productos/destacados/ - Productos destacados
    path('productos/destacados/', CatalogoProductosDestacadosView.as_view(), name='productos-destacados'),
    
    # GET /api/catalogo/productos/nuevos/ - Productos nuevos
    path('productos/nuevos/', CatalogoProductosNuevosView.as_view(), name='productos-nuevos'),
    
    # GET /api/catalogo/productos/mas-vendidos/ - Productos más vendidos
    path('productos/mas-vendidos/', CatalogoProductosMasVendidosView.as_view(), name='productos-mas-vendidos'),
]
