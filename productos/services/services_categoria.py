from productos.models import Categoria
from productos.serializers import CategoriaSerializer
from rest_framework import status


class CategoriaService:
    """Servicio para manejar la lógica de negocio de Categoria"""
    
    @staticmethod
    def listar_categorias():
        """Lista todas las categorías"""
        try:
            categorias = Categoria.objects.all()
            serializer = CategoriaSerializer(categorias, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def crear_categoria(data):
        """Crea una nueva categoría"""
        try:
            serializer = CategoriaSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return True, serializer.data, status.HTTP_201_CREATED
            return False, serializer.errors, status.HTTP_400_BAD_REQUEST
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def obtener_categoria(id_categoria):
        """Obtiene una categoría por ID"""
        try:
            categoria = Categoria.objects.get(idCategoria=id_categoria)
            serializer = CategoriaSerializer(categoria)
            return True, serializer.data, status.HTTP_200_OK
        except Categoria.DoesNotExist:
            return False, {"error": "Categoría no encontrada"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def actualizar_categoria(id_categoria, data):
        """Actualiza una categoría"""
        try:
            categoria = Categoria.objects.get(idCategoria=id_categoria)
            serializer = CategoriaSerializer(categoria, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return True, serializer.data, status.HTTP_200_OK
            return False, serializer.errors, status.HTTP_400_BAD_REQUEST
        except Categoria.DoesNotExist:
            return False, {"error": "Categoría no encontrada"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def eliminar_categoria(id_categoria):
        """Elimina una categoría si no tiene productos asociados"""
        try:
            categoria = Categoria.objects.get(idCategoria=id_categoria)
            
            # Verificar si tiene productos asociados
            if categoria.productos.exists():
                return False, {
                    "error": "No se puede eliminar la categoría porque tiene productos asociados"
                }, status.HTTP_400_BAD_REQUEST
            
            categoria.delete()
            return True, {"mensaje": "Categoría eliminada correctamente"}, status.HTTP_200_OK
        except Categoria.DoesNotExist:
            return False, {"error": "Categoría no encontrada"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def buscar_categoria_por_nombre(nombre):
        """Busca una categoría por nombre exacto"""
        try:
            categoria = Categoria.objects.get(nombre__iexact=nombre)
            serializer = CategoriaSerializer(categoria)
            return True, serializer.data, status.HTTP_200_OK
        except Categoria.DoesNotExist:
            return False, {"error": "Categoría no encontrada"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
