from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductoListCreateView,
    ProductoDetailView,
    ProductoInventoryView,
    VariantStockUpdateView,
    InventarioListView,
    InventarioAjustarView,
    ProductImageUploadView,
    ProductViewSet,
    ProductVariantViewSet,
    ProductImageViewSet,
    inventory_list  # <-- Importar la nueva vista
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'variants', ProductVariantViewSet, basename='variant')
router.register(r'images', ProductImageViewSet, basename='image')

app_name = 'productos'

urlpatterns = [
    path('', ProductoListCreateView.as_view(), name='producto-list-create'),
    path('<int:pk>/', ProductoDetailView.as_view(), name='producto-detail'),
    path('<int:pk>/inventory/', ProductoInventoryView.as_view(), name='producto-inventory'),
    path('variants/<int:variant_id>/stock/', VariantStockUpdateView.as_view(), name='variant-stock-update'),
    path('inventario/', inventory_list, name='inventory-list'),  # <-- Agregar esta línea
    path('inventario/ajustar/', InventarioAjustarView.as_view(), name='inventario-ajustar'),
    path('upload-image/', ProductImageUploadView.as_view(), name='upload-image'),
    path('', include(router.urls)),
]