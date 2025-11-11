from productos.models import Producto, Categoria
from productos.serializers import ProductoSerializer, ProductoDetailSerializer
from rest_framework import status
from django.db.models import Q


class ProductoService:
    """Servicio para manejar la lógica de negocio de Producto"""
    
    @staticmethod
    def listar_productos():
        """Lista todos los productos con información de categoría"""
        try:
            productos = Producto.objects.select_related('categoria').all()
            serializer = ProductoDetailSerializer(productos, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def crear_producto(data):
        """Crea un nuevo producto"""
        try:
            serializer = ProductoSerializer(data=data)
            if serializer.is_valid():
                producto = serializer.save()
                # Retornar con información detallada (incluyendo categoría)
                detail_serializer = ProductoDetailSerializer(producto)
                return True, detail_serializer.data, status.HTTP_201_CREATED
            return False, serializer.errors, status.HTTP_400_BAD_REQUEST
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def obtener_producto(id_producto):
        """Obtiene un producto por ID con información de categoría"""
        try:
            producto = Producto.objects.select_related('categoria').get(idProducto=id_producto)
            serializer = ProductoDetailSerializer(producto)
            return True, serializer.data, status.HTTP_200_OK
        except Producto.DoesNotExist:
            return False, {"error": "Producto no encontrado"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def actualizar_producto(id_producto, data):
        """Actualiza un producto"""
        try:
            producto = Producto.objects.get(idProducto=id_producto)
            serializer = ProductoSerializer(producto, data=data, partial=True)
            if serializer.is_valid():
                producto_actualizado = serializer.save()
                # Retornar con información detallada
                detail_serializer = ProductoDetailSerializer(producto_actualizado)
                return True, detail_serializer.data, status.HTTP_200_OK
            return False, serializer.errors, status.HTTP_400_BAD_REQUEST
        except Producto.DoesNotExist:
            return False, {"error": "Producto no encontrado"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def eliminar_producto(id_producto):
        """Elimina un producto permanentemente"""
        try:
            producto = Producto.objects.get(idProducto=id_producto)
            nombre_producto = producto.nombre
            producto.delete()
            return True, {
                "mensaje": f"Producto '{nombre_producto}' eliminado correctamente"
            }, status.HTTP_200_OK
        except Producto.DoesNotExist:
            return False, {"error": "Producto no encontrado"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def buscar_productos(query):
        """Busca productos por nombre"""
        try:
            productos = Producto.objects.select_related('categoria').filter(
                Q(nombre__icontains=query)
            )
            serializer = ProductoDetailSerializer(productos, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def listar_productos_por_categoria(id_categoria):
        """Lista todos los productos de una categoría específica"""
        try:
            # Verificar que la categoría existe
            categoria = Categoria.objects.get(idCategoria=id_categoria)
            productos = Producto.objects.select_related('categoria').filter(categoria=categoria)
            serializer = ProductoDetailSerializer(productos, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Categoria.DoesNotExist:
            return False, {"error": "Categoría no encontrada"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def actualizar_stock(id_producto, cantidad):
        """Actualiza el stock de un producto"""
        try:
            producto = Producto.objects.get(idProducto=id_producto)
            nuevo_stock = producto.stock + cantidad
            
            if nuevo_stock < 0:
                return False, {
                    "error": "El stock no puede ser negativo"
                }, status.HTTP_400_BAD_REQUEST
            
            producto.stock = nuevo_stock
            producto.save()
            
            serializer = ProductoDetailSerializer(producto)
            return True, serializer.data, status.HTTP_200_OK
        except Producto.DoesNotExist:
            return False, {"error": "Producto no encontrado"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
