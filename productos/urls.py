from django.urls import path
from .views import (
    # Vistas de Categoría
    CategoriaListCreateView,
    CategoriaDetailView,
    CategoriaBuscarView,
    # Vistas de Producto
    ProductoListCreateView,
    ProductoDetailView,
    ProductoBuscarView,
    ProductoPorCategoriaView,
    ProductoActualizarStockView,
)

app_name = 'productos'

urlpatterns = [
    # ==================== RUTAS DE CATEGORIA ====================
    # GET /api/productos/categorias/ - Listar todas las categorías
    # POST /api/productos/categorias/ - Crear una nueva categoría
    path('categorias/', CategoriaListCreateView.as_view(), name='categoria-list-create'),
    
    # GET /api/productos/categorias/<id>/ - Obtener una categoría
    # PUT /api/productos/categorias/<id>/ - Actualizar una categoría completamente
    # PATCH /api/productos/categorias/<id>/ - Actualizar una categoría parcialmente
    # DELETE /api/productos/categorias/<id>/ - Eliminar una categoría
    path('categorias/<int:id_categoria>/', CategoriaDetailView.as_view(), name='categoria-detail'),
    
    # GET /api/productos/categorias/buscar/?nombre=<nombre> - Buscar categoría por nombre
    path('categorias/buscar/', CategoriaBuscarView.as_view(), name='categoria-buscar'),
    
    
    # ==================== RUTAS DE PRODUCTO ====================
    # GET /api/productos/ - Listar todos los productos
    # POST /api/productos/ - Crear un nuevo producto
    path('', ProductoListCreateView.as_view(), name='producto-list-create'),
    
    # GET /api/productos/<id>/ - Obtener un producto
    # PUT /api/productos/<id>/ - Actualizar un producto completamente
    # PATCH /api/productos/<id>/ - Actualizar un producto parcialmente
    # DELETE /api/productos/<id>/ - Eliminar un producto
    path('<int:id_producto>/', ProductoDetailView.as_view(), name='producto-detail'),
    
    # GET /api/productos/buscar/?q=<query> - Buscar productos
    path('buscar/', ProductoBuscarView.as_view(), name='producto-buscar'),
    
    # GET /api/productos/categoria/<id_categoria>/ - Listar productos por categoría
    path('categoria/<int:id_categoria>/', ProductoPorCategoriaView.as_view(), name='producto-por-categoria'),
    
    # PATCH /api/productos/<id>/stock/ - Actualizar stock de un producto
    path('<int:id_producto>/stock/', ProductoActualizarStockView.as_view(), name='producto-actualizar-stock'),
]