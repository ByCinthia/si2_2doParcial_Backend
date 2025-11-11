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
    path('proveedores/', ProveedorListCreateView.as_view(), name='proveedor-list-create'),
    path('proveedores/buscar/', ProveedorBuscarView.as_view(), name='proveedor-buscar'),
    path('proveedores/<int:id_proveedor>/', ProveedorDetailView.as_view(), name='proveedor-detail'),
    
    # ==================== COMPRAS ====================
    path('', CompraListCreateView.as_view(), name='compra-list-create'),
    path('estadisticas/', EstadisticasComprasView.as_view(), name='compras-estadisticas'),
    path('proveedor/<int:id_proveedor>/', ComprasPorProveedorView.as_view(), name='compras-por-proveedor'),
    path('<int:id_compra>/', CompraDetailView.as_view(), name='compra-detail'),
    path('<int:id_compra>/imagen/', CompraActualizarImagenView.as_view(), name='compra-actualizar-imagen'),
]
