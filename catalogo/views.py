from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .service_catalogo import CatalogoService


class CatalogoProductosListView(APIView):
    """
    Vista pública para listar productos del catálogo.
    Permite filtrar por categoría usando query param: ?categoria={id}
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Lista todos los productos o filtra por categoría"""
        categoria_id = request.query_params.get('categoria', None)
        success, data, status = CatalogoService.listar_productos(categoria_id)
        return Response(data, status=status)


class CatalogoProductoDetailView(APIView):
    """Vista pública para obtener detalles de un producto"""
    permission_classes = [AllowAny]
    
    def get(self, request, id_producto):
        """Obtiene un producto específico"""
        success, data, status = CatalogoService.obtener_producto(id_producto)
        return Response(data, status=status)


class CatalogoCategoriasListView(APIView):
    """Vista pública para listar categorías disponibles"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Lista todas las categorías con productos disponibles"""
        success, data, status = CatalogoService.listar_categorias()
        return Response(data, status=status)


class CatalogoProductosDestacadosView(APIView):
    """Vista pública para productos destacados"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Retorna productos destacados"""
        success, data, status = CatalogoService.productos_destacados()
        return Response(data, status=status)


class CatalogoProductosNuevosView(APIView):
    """Vista pública para productos nuevos"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Retorna productos más recientes"""
        success, data, status = CatalogoService.productos_nuevos()
        return Response(data, status=status)


class CatalogoProductosMasVendidosView(APIView):
    """Vista pública para productos más vendidos"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Retorna productos más vendidos"""
        success, data, status = CatalogoService.productos_mas_vendidos()
        return Response(data, status=status)

