from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

from .services.services_categoria import CategoriaService


class CategoriaListCreateView(APIView):
    """Listar y crear categorías"""

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def get(self, request):
        success, data, status_code = CategoriaService.listar_categorias()
        return Response(data, status=status_code)

    def post(self, request):
        success, data, status_code = CategoriaService.crear_categoria(request.data)
        return Response(data, status=status_code)


class CategoriaDetailView(APIView):
    """Obtener, actualizar, eliminar (soft) categoría"""
    permission_classes = [IsAuthenticated]

    def get(self, request, id_categoria):
        success, data, status_code = CategoriaService.obtener_categoria(id_categoria)
        return Response(data, status=status_code)

    def put(self, request, id_categoria):
        success, data, status_code = CategoriaService.actualizar_categoria(id_categoria, request.data)
        return Response(data, status=status_code)

    def patch(self, request, id_categoria):
        success, data, status_code = CategoriaService.actualizar_categoria(id_categoria, request.data)
        return Response(data, status=status_code)

    def delete(self, request, id_categoria):
        success, data, status_code = CategoriaService.eliminar_categoria(id_categoria)
        return Response(data, status=status_code)


class CategoriaBuscarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        nombre = request.query_params.get('nombre', '')
        if not nombre:
            return Response({"error": "Debe proporcionar un nombre"}, status=400)
        success, data, status_code = CategoriaService.buscar_por_nombre(nombre)
        return Response(data, status=status_code)
