from django.db import transaction
from django.shortcuts import get_object_or_404
from productos.models import ProductVariant, Product

class VentaService:
    @staticmethod
    def confirmar_pedido(pedido_id, usuario, pago_data):
        # Import local para evitar errores durante checks/makemigrations
        from .models import Pedido, PedidoItem, Venta, DetalleVenta
        
        pedido = get_object_or_404(Pedido, idPedido=pedido_id)
        
        with transaction.atomic():
            venta = Venta.objects.create(
                usuario=usuario,
                total=pedido.total
            )
            
            for pi in pedido.items.all():
                variant = pi.variante
                if variant:
                    if variant.stock < pi.cantidad:
                        raise ValueError(f"Stock insuficiente para {variant}")
                    variant.stock -= pi.cantidad
                    variant.save()
                    precio = variant.price if hasattr(variant, 'price') and variant.price else pi.precio
                else:
                    precio = pi.precio
                
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=pi.producto,
                    cantidad=pi.cantidad,
                    precio_unitario=precio,
                    subtotal=pi.cantidad * precio
                )
            
            pedido.estado = 'PAGADO'
            pedido.save()
            
            return venta