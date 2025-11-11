from productos.models import Producto, Categoria
from productos.serializers import ProductoDetailSerializer, CategoriaSerializer
from rest_framework import status
from django.db.models import Q


class CatalogoService:
    """Servicio para manejar la lógica de negocio del catálogo público"""
    
    @staticmethod
    def listar_productos(categoria_id=None):
        """
        Lista todos los productos disponibles en el catálogo.
        Opcionalmente filtra por categoría si se proporciona categoria_id.
        """
        try:
            # Filtrar solo productos con stock disponible
            productos = Producto.objects.select_related('categoria').filter(stock__gt=0)
            
            # Filtrar por categoría si se proporciona
            if categoria_id:
                try:
                    categoria_id = int(categoria_id)
                    productos = productos.filter(categoria__idCategoria=categoria_id)
                except (ValueError, TypeError):
                    return False, {"error": "ID de categoría inválido"}, status.HTTP_400_BAD_REQUEST
            
            serializer = ProductoDetailSerializer(productos, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def obtener_producto(id_producto):
        """Obtiene los detalles de un producto específico del catálogo"""
        try:
            producto = Producto.objects.select_related('categoria').get(
                idProducto=id_producto,
                stock__gt=0  # Solo mostrar si tiene stock
            )
            serializer = ProductoDetailSerializer(producto)
            return True, serializer.data, status.HTTP_200_OK
        except Producto.DoesNotExist:
            return False, {"error": "Producto no encontrado o sin stock"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def listar_categorias():
        """Lista todas las categorías que tienen productos con stock"""
        try:
            # Solo mostrar categorías que tengan productos con stock
            categorias = Categoria.objects.filter(
                productos__stock__gt=0
            ).distinct()
            
            serializer = CategoriaSerializer(categorias, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def productos_destacados():
        """
        Retorna productos destacados.
        Criterio: Productos con mayor stock (asumiendo que son los más populares)
        """
        try:
            productos = Producto.objects.select_related('categoria').filter(
                stock__gt=0
            ).order_by('-stock')[:10]  # Top 10 productos con más stock
            
            serializer = ProductoDetailSerializer(productos, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def productos_nuevos():
        """
        Retorna los productos más recientes.
        Criterio: Ordenados por fecha de creación descendente
        """
        try:
            productos = Producto.objects.select_related('categoria').filter(
                stock__gt=0
            ).order_by('-fecha_creacion')[:10]  # Últimos 10 productos creados
            
            serializer = ProductoDetailSerializer(productos, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def productos_mas_vendidos():
        """
        Retorna los productos más vendidos.
        Criterio: Productos con menor stock (asumiendo que han vendido más)
        pero que aún tengan stock disponible.
        """
        try:
            productos = Producto.objects.select_related('categoria').filter(
                stock__gt=0,
                stock__lte=20  # Productos con stock bajo (han vendido más)
            ).order_by('stock')[:10]  # Ordenar por menor stock primero
            
            serializer = ProductoDetailSerializer(productos, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
