from django.db import transaction
from compras.models import Compra, DetalleCompra, Proveedor
from productos.models import Producto
from compras.serializers import (
    CompraSerializer, 
    CrearCompraSerializer,
    ActualizarImagenCompraSerializer
)
from rest_framework import status


class CompraService:
    """Servicio para manejar la lógica de negocio de Compras"""
    
    @staticmethod
    def listar_compras():
        """Lista todas las compras con sus detalles"""
        try:
            compras = Compra.objects.all().select_related('proveedor').prefetch_related('detalles__producto')
            serializer = CompraSerializer(compras, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def obtener_compra(id_compra):
        """Obtiene una compra por ID con todos sus detalles"""
        try:
            compra = Compra.objects.select_related('proveedor').prefetch_related(
                'detalles__producto__categoria'
            ).get(idCompra=id_compra)
            
            serializer = CompraSerializer(compra)
            return True, serializer.data, status.HTTP_200_OK
        except Compra.DoesNotExist:
            return False, {"error": "Compra no encontrada"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    @transaction.atomic
    def crear_compra(data):
        """
        Crea una nueva compra con sus detalles y actualiza el stock de los productos.
        Se ejecuta dentro de una transacción para garantizar consistencia.
        """
        try:
            # Validar datos de entrada
            serializer = CrearCompraSerializer(data=data)
            if not serializer.is_valid():
                return False, serializer.errors, status.HTTP_400_BAD_REQUEST
            
            validated_data = serializer.validated_data
            
            # Obtener proveedor
            proveedor = Proveedor.objects.get(idProveedor=validated_data['proveedor'])
            
            # Crear la compra (sin imagen por ahora)
            compra = Compra.objects.create(
                proveedor=proveedor,
                total=0  # Se calculará con los detalles
            )
            
            # Procesar cada detalle de compra
            total_compra = 0
            detalles_creados = []
            
            for detalle_data in validated_data['detalles']:
                # Obtener producto
                producto = Producto.objects.select_for_update().get(
                    idProducto=detalle_data['producto'].idProducto
                )
                
                # Calcular subtotal
                cantidad = detalle_data['cantidad']
                precio = detalle_data['precio']
                subtotal = cantidad * precio
                
                # Crear detalle de compra
                detalle = DetalleCompra.objects.create(
                    compra=compra,
                    producto=producto,
                    cantidad=cantidad,
                    precio=precio,
                    subtotal=subtotal
                )
                detalles_creados.append(detalle)
                
                # **ACTUALIZAR STOCK DEL PRODUCTO**
                producto.stock += cantidad
                producto.save()
                
                # Acumular total
                total_compra += subtotal
            
            # Actualizar total de la compra
            compra.total = total_compra
            
            # Guardar imagen si se proporciona
            if 'imagen' in validated_data and validated_data['imagen']:
                compra.imagen = validated_data['imagen']
            
            compra.save()
            
            # Retornar compra creada
            compra_serializada = CompraSerializer(compra)
            return True, {
                "mensaje": "Compra registrada correctamente",
                "compra": compra_serializada.data,
                "productos_actualizados": len(detalles_creados)
            }, status.HTTP_201_CREATED
            
        except Proveedor.DoesNotExist:
            return False, {"error": "Proveedor no encontrado"}, status.HTTP_404_NOT_FOUND
        except Producto.DoesNotExist:
            return False, {"error": "Uno o más productos no existen"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def actualizar_imagen_compra(id_compra, imagen):
        """Actualiza la imagen/comprobante de una compra"""
        try:
            compra = Compra.objects.get(idCompra=id_compra)
            
            serializer = ActualizarImagenCompraSerializer(data={'imagen': imagen})
            if not serializer.is_valid():
                return False, serializer.errors, status.HTTP_400_BAD_REQUEST
            
            compra.imagen = serializer.validated_data['imagen']
            compra.save()
            
            compra_serializada = CompraSerializer(compra)
            return True, {
                "mensaje": "Comprobante actualizado correctamente",
                "compra": compra_serializada.data
            }, status.HTTP_200_OK
            
        except Compra.DoesNotExist:
            return False, {"error": "Compra no encontrada"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def eliminar_compra(id_compra):
        """
        Elimina una compra. 
        NOTA: No revierte el stock porque se asume que la compra ya fue procesada.
        Si necesitas revertir stock, debes implementar esa lógica.
        """
        try:
            compra = Compra.objects.get(idCompra=id_compra)
            compra.delete()
            
            return True, {
                "mensaje": "Compra eliminada correctamente"
            }, status.HTTP_200_OK
            
        except Compra.DoesNotExist:
            return False, {"error": "Compra no encontrada"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def listar_compras_por_proveedor(id_proveedor):
        """Lista todas las compras de un proveedor específico"""
        try:
            compras = Compra.objects.filter(
                proveedor__idProveedor=id_proveedor
            ).select_related('proveedor').prefetch_related('detalles__producto')
            
            serializer = CompraSerializer(compras, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def obtener_estadisticas_compras():
        """Obtiene estadísticas generales de compras"""
        try:
            from django.db.models import Sum, Count, Avg
            
            total_compras = Compra.objects.count()
            monto_total = Compra.objects.aggregate(Sum('total'))['total__sum'] or 0
            promedio_compra = Compra.objects.aggregate(Avg('total'))['total__avg'] or 0
            
            # Proveedor con más compras
            proveedor_top = Compra.objects.values(
                'proveedor__nombre'
            ).annotate(
                cantidad=Count('idCompra'),
                total_gastado=Sum('total')
            ).order_by('-cantidad').first()
            
            return True, {
                "total_compras": total_compras,
                "monto_total": round(monto_total, 2),
                "promedio_por_compra": round(promedio_compra, 2),
                "proveedor_top": proveedor_top
            }, status.HTTP_200_OK
            
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
