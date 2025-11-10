from django.urls import path
from .views import (
    ProductoListCreateView,
    ProductoDetailView,
    ProductoInventoryView,
    VariantStockUpdateView,
)

app_name = 'productos'

urlpatterns = [
    path('', ProductoListCreateView.as_view(), name='producto-list-create'),
    path('<int:pk>/', ProductoDetailView.as_view(), name='producto-detail'),
    path('<int:pk>/inventory/', ProductoInventoryView.as_view(), name='producto-inventory'),
    path('variants/<int:variant_id>/stock/', VariantStockUpdateView.as_view(), name='variant-stock-update'),
]