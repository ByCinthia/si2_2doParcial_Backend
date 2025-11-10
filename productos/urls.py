from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    ProductInventoryView,
    VariantStockUpdateView,
)

app_name = 'productos'

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('<int:pk>/inventory/', ProductInventoryView.as_view(), name='product-inventory'),
    path('variants/<int:variant_id>/stock/', VariantStockUpdateView.as_view(), name='variant-stock-update'),
]