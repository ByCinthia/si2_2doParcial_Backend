from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from ..models import Categoria
from ..serializers import CategoriaSerializer


class CategoriaService:
    """Servicio para operaciones CRUD de Categoría"""

    @staticmethod
    def listar_categorias():
        try:
            qs = Categoria.objects.all()
            serializer = CategoriaSerializer(qs, many=True)
            return True, serializer.data, 200
        except Exception as e:
            return False, {"error": f"Error al listar categorías: {str(e)}"}, 500

    @staticmethod
    def obtener_categoria(id_categoria):
        try:
            obj = Categoria.objects.get(idCategoria=id_categoria)
            serializer = CategoriaSerializer(obj)
            return True, serializer.data, 200
        except ObjectDoesNotExist:
            return False, {"error": "Categoría no encontrada"}, 404
        except Exception as e:
            return False, {"error": f"Error al obtener categoría: {str(e)}"}, 500

    @staticmethod
    def crear_categoria(data):
        try:
            serializer = CategoriaSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return True, serializer.data, 201
            return False, serializer.errors, 400
        except IntegrityError:
            return False, {"error": "Ya existe una categoría con ese nombre"}, 400
        except Exception as e:
            return False, {"error": f"Error al crear categoría: {str(e)}"}, 500

    @staticmethod
    def actualizar_categoria(id_categoria, data):
        try:
            obj = Categoria.objects.get(idCategoria=id_categoria)
            serializer = CategoriaSerializer(obj, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return True, serializer.data, 200
            return False, serializer.errors, 400
        except ObjectDoesNotExist:
            return False, {"error": "Categoría no encontrada"}, 404
        except IntegrityError:
            return False, {"error": "Ya existe una categoría con ese nombre"}, 400
        except Exception as e:
            return False, {"error": f"Error al actualizar categoría: {str(e)}"}, 500

    @staticmethod
    def eliminar_categoria(id_categoria):
        try:
            obj = Categoria.objects.get(idCategoria=id_categoria)
            # soft delete: marcar inactivo
            obj.activo = False
            obj.save()
            return True, {"mensaje": "Categoría desactivada correctamente"}, 200
        except ObjectDoesNotExist:
            return False, {"error": "Categoría no encontrada"}, 404
        except Exception as e:
            return False, {"error": f"Error al eliminar categoría: {str(e)}"}, 500

    @staticmethod
    def buscar_por_nombre(nombre):
        try:
            obj = Categoria.objects.get(nombre=nombre)
            serializer = CategoriaSerializer(obj)
            return True, serializer.data, 200
        except ObjectDoesNotExist:
            return False, {"error": "Categoría no encontrada"}, 404
        except Exception as e:
            return False, {"error": f"Error al buscar categoría: {str(e)}"}, 500
