from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .services.services_categoria import CategoriaService
from .services.sevices_producto import ProductoService


# ==================== VISTAS DE CATEGORIA ====================

class CategoriaListCreateView(APIView):
    """Vista para listar y crear categorías"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Lista todas las categorías"""
        success, data, status = CategoriaService.listar_categorias()
        return Response(data, status=status)
    
    def post(self, request):
        """Crea una nueva categoría"""
        success, data, status = CategoriaService.crear_categoria(request.data)
        return Response(data, status=status)


class CategoriaDetailView(APIView):
    """Vista para obtener, actualizar y eliminar una categoría"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_categoria):
        """Obtiene una categoría por ID"""
        success, data, status = CategoriaService.obtener_categoria(id_categoria)
        return Response(data, status=status)
    
    def put(self, request, id_categoria):
        """Actualiza una categoría"""
        success, data, status = CategoriaService.actualizar_categoria(id_categoria, request.data)
        return Response(data, status=status)
    
    def patch(self, request, id_categoria):
        """Actualiza parcialmente una categoría"""
        success, data, status = CategoriaService.actualizar_categoria(id_categoria, request.data)
        return Response(data, status=status)
    
    def delete(self, request, id_categoria):
        """Elimina una categoría"""
        success, data, status = CategoriaService.eliminar_categoria(id_categoria)
        return Response(data, status=status)


class CategoriaBuscarView(APIView):
    """Vista para buscar categoría por nombre"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Busca una categoría por nombre"""
        nombre = request.query_params.get('nombre', '')
        if not nombre:
            return Response({"error": "Debe proporcionar un nombre"}, status=400)
        success, data, status = CategoriaService.buscar_categoria_por_nombre(nombre)
        return Response(data, status=status)


# ==================== VISTAS DE PRODUCTO ====================

class ProductoListCreateView(APIView):
    """Vista para listar y crear productos"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get(self, request):
        """Lista todos los productos"""
        success, data, status = ProductoService.listar_productos()
        return Response(data, status=status)
    
    def post(self, request):
        """Crea un nuevo producto (acepta imagen)"""
        success, data, status = ProductoService.crear_producto(request.data)
        return Response(data, status=status)


class ProductoDetailView(APIView):
    """Vista para obtener, actualizar y eliminar un producto"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get(self, request, id_producto):
        """Obtiene un producto por ID"""
        success, data, status = ProductoService.obtener_producto(id_producto)
        return Response(data, status=status)
    
    def put(self, request, id_producto):
        """Actualiza un producto (acepta imagen)"""
        success, data, status = ProductoService.actualizar_producto(id_producto, request.data)
        return Response(data, status=status)
    
    def patch(self, request, id_producto):
        """Actualiza parcialmente un producto (acepta imagen)"""
        success, data, status = ProductoService.actualizar_producto(id_producto, request.data)
        return Response(data, status=status)
    
    def delete(self, request, id_producto):
        """Elimina un producto"""
        success, data, status = ProductoService.eliminar_producto(id_producto)
        return Response(data, status=status)


class ProductoBuscarView(APIView):
    """Vista para buscar productos"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Busca productos por nombre"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({"error": "Debe proporcionar un término de búsqueda (q)"}, status=400)
        success, data, status = ProductoService.buscar_productos(query)
        return Response(data, status=status)


class ProductoPorCategoriaView(APIView):
    """Vista para listar productos por categoría"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_categoria):
        """Lista todos los productos de una categoría"""
        success, data, status = ProductoService.listar_productos_por_categoria(id_categoria)
        return Response(data, status=status)


class ProductoActualizarStockView(APIView):
    """Vista para actualizar el stock de un producto"""
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, id_producto):
        """Actualiza el stock de un producto"""
        cantidad = request.data.get('cantidad')
        if cantidad is None:
            return Response({"error": "Debe proporcionar la cantidad"}, status=400)
        
        try:
            cantidad = int(cantidad)
        except ValueError:
            return Response({"error": "La cantidad debe ser un número entero"}, status=400)
        
        success, data, status = ProductoService.actualizar_stock(id_producto, cantidad)
        return Response(data, status=status)

