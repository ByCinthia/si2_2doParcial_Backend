from django.db import transaction
from django.conf import settings
from ventas.models import Venta, DetalleVenta, Cuota, MetodoPago
from productos.models import Producto
from ventas.serializers import VentaSerializer, CrearVentaSerializer
from rest_framework import status
from datetime import timedelta
from django.utils import timezone
import stripe

# Configurar Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class VentaService:
    """Servicio para manejar la lógica de negocio de Ventas"""
    
    # Tasas de interés anuales según número de cuotas
    TASAS_INTERES = {
        1: 0.0,    # Al contado: 0% interés
        3: 0.19,   # 3 cuotas: 19% anual
        6: 0.15,   # 6 cuotas: 15% anual
        12: 0.12,  # 12 cuotas: 12% anual
    }
    
    @staticmethod
    def listar_ventas():
        """Lista todas las ventas (solo para administrador)"""
        try:
            ventas = Venta.objects.all().select_related('usuario', 'metodoPago').prefetch_related(
                'detalles__producto',
                'cuotas'
            )
            serializer = VentaSerializer(ventas, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def obtener_estadisticas_ventas():
        """Obtiene estadísticas generales de ventas (solo para administrador)"""
        try:
            from django.db.models import Sum, Count, Avg
            
            total_ventas = Venta.objects.count()
            monto_total = Venta.objects.aggregate(Sum('total'))['total__sum'] or 0
            promedio_venta = Venta.objects.aggregate(Avg('total'))['total__avg'] or 0
            
            # Ventas por método de pago
            ventas_por_metodo = Venta.objects.values(
                'metodoPago__nombre'
            ).annotate(
                cantidad=Count('idVenta'),
                total_recaudado=Sum('total')
            ).order_by('-cantidad')
            
            # Ventas al contado vs cuotas
            ventas_contado = Venta.objects.filter(nrocuotas=1).count()
            ventas_cuotas = Venta.objects.filter(nrocuotas__gt=1).count()
            
            return True, {
                "total_ventas": total_ventas,
                "monto_total": round(monto_total, 2),
                "promedio_por_venta": round(promedio_venta, 2),
                "ventas_por_metodo": list(ventas_por_metodo),
                "ventas_contado": ventas_contado,
                "ventas_en_cuotas": ventas_cuotas
            }, status.HTTP_200_OK
            
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def listar_ventas_usuario(usuario):
        """Lista todas las ventas de un usuario"""
        try:
            ventas = Venta.objects.filter(usuario=usuario).select_related(
                'metodoPago'
            ).prefetch_related('detalles__producto', 'cuotas')
            serializer = VentaSerializer(ventas, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def obtener_venta(id_venta):
        """Obtiene una venta por ID"""
        try:
            venta = Venta.objects.select_related('usuario', 'metodoPago').prefetch_related(
                'detalles__producto__categoria',
                'cuotas'
            ).get(idVenta=id_venta)
            
            serializer = VentaSerializer(venta)
            return True, serializer.data, status.HTTP_200_OK
        except Venta.DoesNotExist:
            return False, {"error": "Venta no encontrada"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def crear_checkout_session_contado(data, usuario):
        """
        Genera un Stripe Checkout Session para PAGO AL CONTADO (1 cuota).
        La venta se crea DESPUÉS de que Stripe confirme el pago via webhook.
        SOLO se usa cuando nrocuotas == 1.
        """
        try:
            # Validar datos de entrada
            serializer = CrearVentaSerializer(data=data)
            if not serializer.is_valid():
                return False, serializer.errors, status.HTTP_400_BAD_REQUEST
            
            validated_data = serializer.validated_data
            
            # Verificar que sea pago al contado
            nrocuotas = validated_data['nrocuotas']
            if nrocuotas != 1:
                return False, {"error": "Este método es solo para pago al contado (1 cuota)"}, status.HTTP_400_BAD_REQUEST
            
            # Obtener método de pago
            metodo_pago = MetodoPago.objects.get(idMetodoPago=validated_data['metodoPago'])
            
            # Calcular subtotal y validar stock
            subtotal = 0
            line_items = []
            productos_metadata = []
            
            for detalle_data in validated_data['detalles']:
                producto = Producto.objects.get(idProducto=detalle_data['producto'])
                
                # Verificar stock
                if producto.stock < detalle_data['cantidad']:
                    return False, {
                        "error": f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}"
                    }, status.HTTP_400_BAD_REQUEST
                
                subtotal_producto = producto.precio * detalle_data['cantidad']
                subtotal += subtotal_producto
                
                # Line item para Stripe
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': producto.nombre,
                            'description': f"Cantidad: {detalle_data['cantidad']}"
                        },
                        'unit_amount': int(producto.precio * 100),  # Stripe usa centavos
                    },
                    'quantity': detalle_data['cantidad'],
                })
                
                # Guardar info del producto para metadata
                productos_metadata.append({
                    'producto_id': producto.idProducto,
                    'cantidad': detalle_data['cantidad'],
                    'precio': float(producto.precio)
                })
            
            total = subtotal  # Sin interés para pago al contado
            
            # Crear Stripe Checkout Session
            import json
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=f"{settings.FRONTEND_URL}/ventas/exito?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/ventas/cancelado",
                metadata={
                    'tipo': 'venta_contado',
                    'usuario_id': usuario.idUsuario,
                    'metodo_pago_id': metodo_pago.idMetodoPago,
                    'nrocuotas': 1,
                    'subtotal': str(subtotal),
                    'interes': '0.0',
                    'total': str(total),
                    'productos': json.dumps(productos_metadata)
                }
            )
            
            return True, {
                "mensaje": "Pago al contado - Checkout creado",
                "checkout_url": checkout_session.url,
                "session_id": checkout_session.id,
                "total": round(total, 2),
                "subtotal": round(subtotal, 2),
                "interes": 0.0,
                "nrocuotas": 1,
                "nota": "Complete el pago para confirmar su compra"
            }, status.HTTP_200_OK
            
        except MetodoPago.DoesNotExist:
            return False, {"error": "Método de pago no encontrado"}, status.HTTP_404_NOT_FOUND
        except Producto.DoesNotExist:
            return False, {"error": "Uno o más productos no existen"}, status.HTTP_404_NOT_FOUND
        except stripe.error.StripeError as e:
            return False, {"error": f"Error de Stripe: {str(e)}"}, status.HTTP_500_INTERNAL_SERVER_ERROR
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    @transaction.atomic
    def crear_venta_con_cuotas(data, usuario):
        """
        Crea una venta CON CUOTAS (3, 6 o 12 cuotas) INMEDIATAMENTE.
        La venta se registra en la BD sin esperar pago de Stripe.
        Las cuotas se pagan posteriormente de forma individual.
        """
        try:
            # Validar datos de entrada
            serializer = CrearVentaSerializer(data=data)
            if not serializer.is_valid():
                return False, serializer.errors, status.HTTP_400_BAD_REQUEST
            
            validated_data = serializer.validated_data
            
            # Verificar que sea venta con cuotas
            nrocuotas = validated_data['nrocuotas']
            if nrocuotas == 1:
                return False, {"error": "Para pago al contado use el flujo de Stripe Checkout"}, status.HTTP_400_BAD_REQUEST
            
            # Obtener método de pago
            metodo_pago = MetodoPago.objects.get(idMetodoPago=validated_data['metodoPago'])
            
            # Calcular subtotal de los productos
            subtotal = 0
            productos_validados = []
            
            for detalle_data in validated_data['detalles']:
                producto = Producto.objects.select_for_update().get(
                    idProducto=detalle_data['producto']
                )
                
                # Verificar stock
                if producto.stock < detalle_data['cantidad']:
                    return False, {
                        "error": f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}"
                    }, status.HTTP_400_BAD_REQUEST
                
                subtotal_producto = producto.precio * detalle_data['cantidad']
                subtotal += subtotal_producto
                
                productos_validados.append({
                    'producto': producto,
                    'cantidad': detalle_data['cantidad'],
                    'precio': producto.precio,
                    'subtotal': subtotal_producto
                })
            
            # Calcular interés según número de cuotas
            tasa_interes = VentaService.TASAS_INTERES.get(nrocuotas, 0.0)
            interes_calculado = subtotal * tasa_interes * (nrocuotas / 12)
            total = subtotal + interes_calculado
            
            # Crear la venta
            venta = Venta.objects.create(
                usuario=usuario,
                metodoPago=metodo_pago,
                subtotal=subtotal,
                interes=tasa_interes,
                total=total,
                nrocuotas=nrocuotas
            )
            
            # Crear detalles de venta y actualizar stock
            for producto_data in productos_validados:
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto_data['producto'],
                    cantidad=producto_data['cantidad'],
                    precio=producto_data['precio'],
                    subtotal=producto_data['subtotal']
                )
                
                # Actualizar stock del producto
                producto_data['producto'].stock -= producto_data['cantidad']
                producto_data['producto'].save()
            
            # Generar cuotas
            monto_cuota = total / nrocuotas
            fecha_vencimiento = timezone.now().date()
            
            for i in range(1, nrocuotas + 1):
                # Vencimiento cada 30 días
                fecha_vencimiento = fecha_vencimiento + timedelta(days=30)
                
                Cuota.objects.create(
                    venta=venta,
                    numero_cuota=i,
                    monto=round(monto_cuota, 2),
                    fecha_vencimiento=fecha_vencimiento,
                    pagada=False
                )
            
            # Retornar venta creada
            venta_serializada = VentaSerializer(venta)
            return True, {
                "mensaje": "Venta con cuotas creada exitosamente",
                "venta": venta_serializada.data,
                "productos_comprados": len(productos_validados),
                "cuotas_generadas": nrocuotas,
                "monto_por_cuota": round(monto_cuota, 2),
                "nota": "Ahora puede pagar cada cuota individualmente usando los endpoints de pago"
            }, status.HTTP_201_CREATED
            
        except MetodoPago.DoesNotExist:
            return False, {"error": "Método de pago no encontrado"}, status.HTTP_404_NOT_FOUND
        except Producto.DoesNotExist:
            return False, {"error": "Uno o más productos no existen"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    @transaction.atomic
    def crear_venta_desde_webhook(session_data):
        """
        Crea la venta AL CONTADO después de que Stripe confirme el pago exitoso.
        Llamado desde el webhook de Stripe.
        SOLO para ventas de 1 cuota (pago al contado).
        """
        try:
            metadata = session_data['metadata']
            
            # Extraer datos del metadata
            usuario_id = int(metadata['usuario_id'])
            metodo_pago_id = int(metadata['metodo_pago_id'])
            nrocuotas = int(metadata['nrocuotas'])  # Debe ser 1
            subtotal = float(metadata['subtotal'])
            interes_calculado = float(metadata['interes'])  # Debe ser 0.0
            total = float(metadata['total'])
            
            import json
            productos_data = json.loads(metadata['productos'])
            
            # Obtener usuario y método de pago
            from usuarios.models import Usuario
            usuario = Usuario.objects.get(idUsuario=usuario_id)
            metodo_pago = MetodoPago.objects.get(idMetodoPago=metodo_pago_id)
            
            # Crear la venta al contado
            venta = Venta.objects.create(
                usuario=usuario,
                metodoPago=metodo_pago,
                subtotal=subtotal,
                interes=0.0,  # Sin interés para pago al contado
                total=total,
                nrocuotas=1,
                stripe_checkout_session_id=session_data['id']
            )
            
            # Crear detalles de venta y actualizar stock
            for producto_info in productos_data:
                producto = Producto.objects.select_for_update().get(
                    idProducto=producto_info['producto_id']
                )
                
                cantidad = producto_info['cantidad']
                precio = producto_info['precio']
                subtotal_producto = precio * cantidad
                
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio=precio,
                    subtotal=subtotal_producto
                )
                
                # Actualizar stock
                producto.stock -= cantidad
                producto.save()
            
            # NO generar cuotas para pago al contado
            # La venta queda completamente pagada
            
            print(f"✅ Venta al contado {venta.idVenta} creada y pagada exitosamente desde webhook")
            return True, venta
            
        except Exception as e:
            print(f"❌ Error creando venta al contado desde webhook: {str(e)}")
            return False, None
