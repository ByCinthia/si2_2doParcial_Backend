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

    @staticmethod
    def listar_todo_inventario():
        """Lista todas las variantes con información del producto y categoría"""
        try:
            from ..serializers import InventoryVariantSerializer
            variants = ProductVariant.objects.select_related('product', 'product__categoria').all()
            serializer = InventoryVariantSerializer(variants, many=True)
            return True, serializer.data, 200
        except Exception as e:
            return False, {"error": f"Error al listar inventario global: {str(e)}"}, 500

    @staticmethod
    def ajustar_stock(variant_id, delta=None, stock=None, usuario=None, motivo=None):
        """Ajusta el stock de una variante. Si delta es proporcionado, suma (puede ser negativo). Si stock es proporcionado, lo reemplaza.
        Usa select_for_update en una transacción para evitar condiciones de carrera."""
        from django.db import transaction
        try:
            with transaction.atomic():
                variant = ProductVariant.objects.select_for_update().get(pk=variant_id)
                previous = variant.stock

                if delta is not None:
                    try:
                        d = int(delta)
                    except Exception:
                        d = int(float(delta))
                    # ensure minimum stock is 2
                    variant.stock = max(2, variant.stock + d)
                    used_delta = variant.stock - previous
                elif stock is not None:
                    # set absolute but enforce minimum 2
                    new_stock = int(stock)
                    if new_stock < 2:
                        new_stock = 2
                    variant.stock = new_stock
                    used_delta = variant.stock - previous
                else:
                    return False, {"error": "Proporciona 'delta' o 'stock'"}, 400

                variant.save()

                # Registrar movimiento (si el modelo existe)
                try:
                    from ..models import InventoryMovement
                    InventoryMovement.objects.create(
                        variant=variant,
                        usuario=usuario,
                        previous_stock=previous,
                        new_stock=variant.stock,
                        delta=used_delta,
                        motivo=motivo,
                    )
                except Exception:
                    # No queremos que un error en el logging rompa la operación
                    pass

                serializer = ProductVariantSerializer(variant)
                return True, serializer.data, 200
        except ProductVariant.DoesNotExist:
            return False, {"error": "Variante no encontrada"}, 404
        except Exception as e:
            return False, {"error": f"Error al ajustar stock: {str(e)}"}, 500
