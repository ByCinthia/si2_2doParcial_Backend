from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from compras.services.service_proveedor import ProveedorService
from compras.services.service_compra import CompraService
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


# ==================== PROVEEDORES ====================

class ProveedorListCreateView(APIView):
    """
    GET /api/compras/proveedores/ - Lista todos los proveedores
    POST /api/compras/proveedores/ - Crea un nuevo proveedor
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        success, result, status_code = ProveedorService.listar_proveedores()
        return Response(result, status=status_code)
    
    def post(self, request):
        success, result, status_code = ProveedorService.crear_proveedor(request.data)
        return Response(result, status=status_code)


class ProveedorDetailView(APIView):
    """
    GET /api/compras/proveedores/{id}/ - Obtiene un proveedor
    PUT /api/compras/proveedores/{id}/ - Actualiza un proveedor
    DELETE /api/compras/proveedores/{id}/ - Elimina un proveedor
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_proveedor):
        success, result, status_code = ProveedorService.obtener_proveedor(id_proveedor)
        return Response(result, status=status_code)
    
    def put(self, request, id_proveedor):
        success, result, status_code = ProveedorService.actualizar_proveedor(id_proveedor, request.data)
        return Response(result, status=status_code)
    
    def delete(self, request, id_proveedor):
        success, result, status_code = ProveedorService.eliminar_proveedor(id_proveedor)
        return Response(result, status=status_code)


class ProveedorBuscarView(APIView):
    """
    GET /api/compras/proveedores/buscar/?q=nombre
    Busca proveedores por nombre o email
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({"error": "Parámetro 'q' requerido"}, status=400)
        
        success, result, status_code = ProveedorService.buscar_proveedores(query)
        return Response(result, status=status_code)


# ==================== COMPRAS ====================

class CompraListCreateView(APIView):
    """
    GET /api/compras/ - Lista todas las compras
    POST /api/compras/ - Crea una nueva compra (con detalles y actualización de stock)
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get(self, request):
        success, result, status_code = CompraService.listar_compras()
        return Response(result, status=status_code)
    
    def post(self, request):
        success, result, status_code = CompraService.crear_compra(request.data)
        return Response(result, status=status_code)


class CompraDetailView(APIView):
    """
    GET /api/compras/{id}/ - Obtiene una compra con sus detalles
    DELETE /api/compras/{id}/ - Elimina una compra
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_compra):
        success, result, status_code = CompraService.obtener_compra(id_compra)
        return Response(result, status=status_code)
    
    def delete(self, request, id_compra):
        success, result, status_code = CompraService.eliminar_compra(id_compra)
        return Response(result, status=status_code)


class CompraActualizarImagenView(APIView):
    """
    PUT /api/compras/{id}/imagen/
    Actualiza el comprobante/imagen de una compra
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def put(self, request, id_compra):
        if 'imagen' not in request.FILES:
            return Response({"error": "Debe proporcionar una imagen"}, status=400)
        
        imagen = request.FILES['imagen']
        success, result, status_code = CompraService.actualizar_imagen_compra(id_compra, imagen)
        return Response(result, status=status_code)


class ComprasPorProveedorView(APIView):
    """
    GET /api/compras/proveedor/{id_proveedor}/
    Lista todas las compras de un proveedor específico
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_proveedor):
        success, result, status_code = CompraService.listar_compras_por_proveedor(id_proveedor)
        return Response(result, status=status_code)


class EstadisticasComprasView(APIView):
    """
    GET /api/compras/estadisticas/
    Obtiene estadísticas generales de compras
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        success, result, status_code = CompraService.obtener_estadisticas_compras()
        return Response(result, status=status_code)
