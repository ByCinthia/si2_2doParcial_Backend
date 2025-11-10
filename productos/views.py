from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
import logging

from .services.services_producto import ProductoService
from .serializers import ProductListSerializer, ProductDetailSerializer, ProductVariantSerializer
from .models import ProductVariant

logger = logging.getLogger(__name__)


class ProductoListCreateView(APIView):
    """Listar y crear productos"""

    def get_permissions(self):
        # permitir lectura pública, creación requiere autenticación
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        success, data, status_code = ProductoService.listar_productos()
        return Response(data, status=status_code)

    def post(self, request):
        success, data, status_code = ProductoService.crear_producto(request.data)
        return Response(data, status=status_code)


class ProductoDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        success, data, status_code = ProductoService.obtener_producto(pk)
        return Response(data, status=status_code)

    def put(self, request, pk):
        success, data, status_code = ProductoService.actualizar_producto(pk, request.data)
        return Response(data, status=status_code)

    def patch(self, request, pk):
        success, data, status_code = ProductoService.actualizar_producto(pk, request.data)
        return Response(data, status=status_code)

    def delete(self, request, pk):
        success, data, status_code = ProductoService.eliminar_producto(pk)
        return Response(data, status=status_code)


class ProductoInventoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        success, data, status_code = ProductoService.listar_inventario(pk)
        return Response(data, status=status_code)


class VariantStockUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, variant_id):
        variant = get_object_or_404(ProductVariant, pk=variant_id)
        serializer = ProductVariantSerializer(variant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
