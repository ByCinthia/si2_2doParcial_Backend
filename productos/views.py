from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Product, ProductVariant
from .serializers import ProductListSerializer, ProductDetailSerializer, ProductVariantSerializer

# Create your views here.

class ProductListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        qs = Product.objects.filter(active=True).prefetch_related('images','variants')
        serializer = ProductListSerializer(qs, many=True)
        return Response(serializer.data)

class ProductDetailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk):
        product = get_object_or_404(Product.objects.prefetch_related('images','variants'), pk=pk, active=True)
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)

class ProductInventoryView(APIView):
    """
    GET /api/productos/<pk>/inventory/  -> lista variantes con stock
    """
    permission_classes = [AllowAny]
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        variants = product.variants.all()
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)

class VariantStockUpdateView(APIView):
    """
    PATCH /api/productos/variants/<variant_id>/stock/ -> actualizar stock (body: {"stock": 10})
    Requiere autenticación (IsAuthenticated) o cambiar según tu lógica.
    """
    permission_classes = [IsAuthenticated]
    def patch(self, request, variant_id):
        variant = get_object_or_404(ProductVariant, pk=variant_id)
        serializer = ProductVariantSerializer(variant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
