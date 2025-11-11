from django.db import transaction
from django.shortcuts import get_object_or_404
from productos.models import ProductVariant, Product
from .models import Pedido, PedidoItem, Venta, VentaItem

class VentaService:
    @staticmethod
    def confirmar_pedido(pedido_id, usuario_vendedor=None, pago_info=None):
        pedido = get_object_or_404(Pedido, idPedido=pedido_id)
        if pedido.estado != 'CREADO':
            return False, "Pedido no en estado CREADO"

        with transaction.atomic():
            venta = Venta.objects.create(
                pedido=pedido,
                cliente=pedido.cliente,
                vendedor=usuario_vendedor,
                total=0
            )
            total = 0
            for pi in pedido.items.select_related('variante','producto').all():
                # comprobar stock en variante si existe, sino en producto (si gestionas stock por variante)
                variant = pi.variante
                if variant:
                    if variant.stock < pi.cantidad:
                        raise ValueError(f"Stock insuficiente para {variant}")
                    variant.stock -= pi.cantidad
                    variant.save()
                    precio = variant.price if getattr(variant, 'price', None) is not None else pi.precio
                else:
                    # si no hay variantes, podrías tener stock en product.stock
                    producto = pi.producto
                    # opcional: manejar stock en producto
                    precio = pi.precio

                VentaItem.objects.create(
                    venta=venta,
                    producto=pi.producto,
                    variante=pi.variante,
                    nombre=pi.nombre,
                    cantidad=pi.cantidad,
                    precio_unitario=pi.precio
                )
                total += pi.subtotal()

            venta.total = total
            venta.save()

            pedido.estado = 'PAGADO'
            pedido.save()

            # aquí puedes almacenar info de pago (pago_info) o emitir señal/nota
            return True, venta