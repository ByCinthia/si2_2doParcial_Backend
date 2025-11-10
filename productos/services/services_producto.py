from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from ..models import Product, ProductVariant
from ..serializers import ProductListSerializer, ProductDetailSerializer, ProductVariantSerializer


class ProductoService:
    """Servicio para lógica de negocio de Productos"""

    @staticmethod
    def listar_productos():
        try:
            qs = Product.objects.filter(active=True).prefetch_related('images', 'variants', 'categoria')
            serializer = ProductListSerializer(qs, many=True)
            return True, serializer.data, 200
        except Exception as e:
            return False, {"error": f"Error al listar productos: {str(e)}"}, 500

    @staticmethod
    def obtener_producto(pk):
        try:
            obj = Product.objects.prefetch_related('images', 'variants').get(pk=pk, active=True)
            serializer = ProductDetailSerializer(obj)
            return True, serializer.data, 200
        except ObjectDoesNotExist:
            return False, {"error": "Producto no encontrado"}, 404
        except Exception as e:
            return False, {"error": f"Error al obtener producto: {str(e)}"}, 500

    @staticmethod
    def crear_producto(data):
        try:
            serializer = ProductDetailSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return True, serializer.data, 201
            return False, serializer.errors, 400
        except IntegrityError:
            return False, {"error": "Error de integridad al crear producto"}, 400
        except Exception as e:
            return False, {"error": f"Error al crear producto: {str(e)}"}, 500

    @staticmethod
    def actualizar_producto(pk, data):
        try:
            obj = Product.objects.get(pk=pk)
            serializer = ProductDetailSerializer(obj, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return True, serializer.data, 200
            return False, serializer.errors, 400
        except ObjectDoesNotExist:
            return False, {"error": "Producto no encontrado"}, 404
        except IntegrityError:
            return False, {"error": "Error de integridad al actualizar producto"}, 400
        except Exception as e:
            return False, {"error": f"Error al actualizar producto: {str(e)}"}, 500

    @staticmethod
    def eliminar_producto(pk):
        try:
            obj = Product.objects.get(pk=pk)
            # soft delete: marcar inactive
            obj.active = False
            obj.save()
            return True, {"mensaje": "Producto desactivado correctamente"}, 200
        except ObjectDoesNotExist:
            return False, {"error": "Producto no encontrado"}, 404
        except Exception as e:
            return False, {"error": f"Error al eliminar producto: {str(e)}"}, 500

    @staticmethod
    def listar_inventario(pk):
        try:
            obj = Product.objects.get(pk=pk)
            serializer = ProductVariantSerializer(obj.variants.all(), many=True)
            return True, serializer.data, 200
        except ObjectDoesNotExist:
            return False, {"error": "Producto no encontrado"}, 404
        except Exception as e:
            return False, {"error": f"Error al listar inventario: {str(e)}"}, 500
