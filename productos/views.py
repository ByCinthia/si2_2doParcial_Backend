from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from usuarios.permissions import CanManageUsers
import logging

from .services.services_producto import ProductoService
from .serializers import ProductListSerializer, ProductDetailSerializer, ProductVariantSerializer
from .models import ProductVariant, ProductImage
from .serializers_inventory import ProductImageSerializer

logger = logging.getLogger(__name__)


class ProductoListCreateView(APIView):
    """Listar y crear productos"""

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        try:
            success, data, status_code = ProductoService.listar_productos()
            return Response(data, status=status_code)
        except Exception as e:
            # queda en logs completos en la consola de runserver
            logger.exception("Error al listar productos (GET /api/productos/)")
            return Response(
                {"error": "Error interno al listar productos. Revisa logs en el servidor."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        try:
            success, data, status_code = ProductoService.crear_producto(request.data)
            return Response(data, status=status_code)
        except Exception:
            logger.exception("Error creando producto")
            return Response({"error":"Error interno al crear producto"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


class InventarioListView(APIView):
    """Lista todas las variantes (inventario global)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        success, data, status_code = ProductoService.listar_todo_inventario()
        return Response(data, status=status_code)


class InventarioAjustarView(APIView):
    """Ajusta stock: body -> { "variant_id": int, "delta": int } o { "variant_id": int, "stock": int }
    Solo usuarios con permiso pueden ajustar inventario."""
    permission_classes = [CanManageUsers]

    def post(self, request):
        variant_id = request.data.get('variant_id')
        delta = request.data.get('delta')
        stock = request.data.get('stock')
        motivo = request.data.get('motivo')

        if not variant_id:
            return Response({"error": "variant_id requerido"}, status=400)

        success, data, status_code = ProductoService.ajustar_stock(variant_id, delta=delta, stock=stock, usuario=getattr(request, 'user', None), motivo=motivo)
        return Response(data, status=status_code)


class ProductImageUploadView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        """
        Espera multipart/form-data con:
        - product: id del producto
        - image: archivo de imagen
        - alt_text, is_main (opcional)
        """
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
