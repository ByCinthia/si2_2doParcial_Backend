from django.urls import path
from .views import (
    ProductoListCreateView,
    ProductoDetailView,
    ProductoInventoryView,
    VariantStockUpdateView,
    InventarioListView,
    InventarioAjustarView,
    ProductImageUploadView,
)

app_name = 'productos'

urlpatterns = [
    path('', ProductoListCreateView.as_view(), name='producto-list-create'),
    path('<int:pk>/', ProductoDetailView.as_view(), name='producto-detail'),
    path('<int:pk>/inventory/', ProductoInventoryView.as_view(), name='producto-inventory'),
    path('variants/<int:variant_id>/stock/', VariantStockUpdateView.as_view(), name='variant-stock-update'),
    # Inventario global: listar y ajustar
    path('inventory/all/', InventarioListView.as_view(), name='inventario-list'),
    path('inventory/adjust/', InventarioAjustarView.as_view(), name='inventario-adjust'),
    path('images/upload/', ProductImageUploadView.as_view(), name='product-image-upload'),
]