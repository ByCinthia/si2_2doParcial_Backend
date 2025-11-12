from django.urls import path
from .views import (
    # Proveedores
    ProveedorListCreateView,
    ProveedorDetailView,
    ProveedorBuscarView,
    
    # Compras
    CompraListCreateView,
    CompraDetailView,
    CompraActualizarImagenView,
    ComprasPorProveedorView,
    EstadisticasComprasView,
)

urlpatterns = [
    # ==================== PROVEEDORES ====================
    # GET /api/compras/proveedores/ - Listar todos los proveedores
    # POST /api/compras/proveedores/ - Crear un nuevo proveedor
    path('proveedores/', ProveedorListCreateView.as_view(), name='proveedor-list-create'),
    
    # GET /api/compras/proveedores/buscar/?q={query} - Buscar proveedores por nombre o email
    path('proveedores/buscar/', ProveedorBuscarView.as_view(), name='proveedor-buscar'),
    
    # GET /api/compras/proveedores/{id}/ - Obtener un proveedor
    # PUT /api/compras/proveedores/{id}/ - Actualizar proveedor completamente
    # PATCH /api/compras/proveedores/{id}/ - Actualizar proveedor parcialmente
    # DELETE /api/compras/proveedores/{id}/ - Eliminar proveedor
    path('proveedores/<int:id_proveedor>/', ProveedorDetailView.as_view(), name='proveedor-detail'),
    
    # ==================== COMPRAS ====================
    # GET /api/compras/ - Listar todas las compras
    # POST /api/compras/ - Crear una nueva compra (con detalles y actualización de stock)
    path('', CompraListCreateView.as_view(), name='compra-list-create'),
    
    # GET /api/compras/estadisticas/ - Obtener estadísticas generales de compras
    path('estadisticas/', EstadisticasComprasView.as_view(), name='compras-estadisticas'),
    
    # GET /api/compras/proveedor/{id_proveedor}/ - Listar compras por proveedor
    path('proveedor/<int:id_proveedor>/', ComprasPorProveedorView.as_view(), name='compras-por-proveedor'),
    
    # GET /api/compras/{id}/ - Obtener una compra con sus detalles
    # PUT /api/compras/{id}/ - Actualizar compra (proveedor y/o imagen)
    # PATCH /api/compras/{id}/ - Actualizar compra parcialmente
    # DELETE /api/compras/{id}/ - Eliminar compra y todos sus detalles
    path('<int:id_compra>/', CompraDetailView.as_view(), name='compra-detail'),
    
    # PUT /api/compras/{id}/imagen/ - Actualizar solo la imagen/comprobante de una compra
    path('<int:id_compra>/imagen/', CompraActualizarImagenView.as_view(), name='compra-actualizar-imagen'),
]
