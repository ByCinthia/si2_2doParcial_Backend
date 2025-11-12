from django.conf import settings
from ventas.models import Cuota
from ventas.serializers import CuotaSerializer
from rest_framework import status
from django.utils import timezone
import stripe

# Configurar Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class CuotaService:
    """Servicio para manejar cuotas y pagos con Stripe"""
    
    @staticmethod
    def listar_cuotas_venta(id_venta):
        """Lista todas las cuotas de una venta"""
        try:
            cuotas = Cuota.objects.filter(venta__idVenta=id_venta).order_by('numero_cuota')
            serializer = CuotaSerializer(cuotas, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def listar_cuotas_usuario(usuario):
        """Lista todas las cuotas de un usuario"""
        try:
            cuotas = Cuota.objects.filter(
                venta__usuario=usuario
            ).select_related('venta').order_by('fecha_vencimiento')
            serializer = CuotaSerializer(cuotas, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def listar_todas_cuotas():
        """Lista todas las cuotas del sistema (solo para administrador)"""
        try:
            cuotas = Cuota.objects.all().select_related(
                'venta__usuario',
                'venta__metodoPago'
            ).order_by('fecha_vencimiento')
            serializer = CuotaSerializer(cuotas, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def listar_cuotas_pendientes():
        """Lista todas las cuotas pendientes del sistema (solo para administrador)"""
        try:
            cuotas = Cuota.objects.filter(
                pagada=False
            ).select_related('venta__usuario', 'venta__metodoPago').order_by('fecha_vencimiento')
            serializer = CuotaSerializer(cuotas, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def listar_cuotas_vencidas():
        """Lista todas las cuotas vencidas del sistema (solo para administrador)"""
        try:
            from django.utils import timezone
            cuotas = Cuota.objects.filter(
                pagada=False,
                fecha_vencimiento__lt=timezone.now().date()
            ).select_related('venta__usuario', 'venta__metodoPago').order_by('fecha_vencimiento')
            serializer = CuotaSerializer(cuotas, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def obtener_estadisticas_cuotas():
        """Obtiene estadísticas de cuotas (solo para administrador)"""
        try:
            from django.db.models import Sum, Count
            from django.utils import timezone
            
            total_cuotas = Cuota.objects.count()
            cuotas_pagadas = Cuota.objects.filter(pagada=True).count()
            cuotas_pendientes = Cuota.objects.filter(pagada=False).count()
            cuotas_vencidas = Cuota.objects.filter(
                pagada=False,
                fecha_vencimiento__lt=timezone.now().date()
            ).count()
            
            monto_total_pendiente = Cuota.objects.filter(pagada=False).aggregate(
                Sum('monto')
            )['monto__sum'] or 0
            
            monto_total_pagado = Cuota.objects.filter(pagada=True).aggregate(
                Sum('monto')
            )['monto__sum'] or 0
            
            return True, {
                "total_cuotas": total_cuotas,
                "cuotas_pagadas": cuotas_pagadas,
                "cuotas_pendientes": cuotas_pendientes,
                "cuotas_vencidas": cuotas_vencidas,
                "monto_total_pendiente": round(monto_total_pendiente, 2),
                "monto_total_pagado": round(monto_total_pagado, 2)
            }, status.HTTP_200_OK
            
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def listar_cuotas_pendientes_usuario(usuario):
        """Lista cuotas pendientes de pago de un usuario"""
        try:
            cuotas = Cuota.objects.filter(
                venta__usuario=usuario,
                pagada=False
            ).select_related('venta').order_by('fecha_vencimiento')
            serializer = CuotaSerializer(cuotas, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def obtener_cuota(id_cuota):
        """Obtiene una cuota por ID"""
        try:
            cuota = Cuota.objects.select_related('venta__usuario').get(idCuota=id_cuota)
            serializer = CuotaSerializer(cuota)
            return True, serializer.data, status.HTTP_200_OK
        except Cuota.DoesNotExist:
            return False, {"error": "Cuota no encontrada"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def crear_payment_intent_cuota(cuota):
        """
        Crea un Payment Intent para pagar una cuota DENTRO de Flutter.
        Retorna el client_secret para usar con flutter_stripe.
        """
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(cuota.monto * 100),  # Convertir a centavos
                currency='usd',
                payment_method_types=['card'],
                metadata={
                    'cuota_id': str(cuota.idCuota),
                    'venta_id': str(cuota.venta.idVenta),
                    'usuario_id': str(cuota.venta.usuario.idUsuario),
                    'numero_cuota': str(cuota.numero_cuota)
                },
                description=f'Cuota {cuota.numero_cuota}/{cuota.venta.nrocuotas} - Venta {cuota.venta.idVenta}'
            )
            
            # Guardar payment_intent_id
            cuota.stripe_payment_intent_id = payment_intent.id
            cuota.save()
            
            return True, {
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id,
                'monto': cuota.monto,
                'cuota': CuotaSerializer(cuota).data
            }, status.HTTP_200_OK
            
        except stripe.error.StripeError as e:
            return False, {"error": f"Error de Stripe: {str(e)}"}, status.HTTP_400_BAD_REQUEST
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def generar_link_pago_cuota(cuota):
        """
        Genera un link de pago (Hosted Checkout) para pagar una cuota en NAVEGADOR.
        El usuario sale de la app y paga en una página de Stripe.
        """
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Cuota {cuota.numero_cuota} de {cuota.venta.nrocuotas}',
                            'description': f'Venta #{cuota.venta.idVenta} - Vencimiento: {cuota.fecha_vencimiento}'
                        },
                        'unit_amount': int(cuota.monto * 100),  # Centavos
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'{settings.FRONTEND_URL}/pago-exitoso?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'{settings.FRONTEND_URL}/pago-cancelado',
                metadata={
                    'cuota_id': str(cuota.idCuota),
                    'venta_id': str(cuota.venta.idVenta),
                    'usuario_id': str(cuota.venta.usuario.idUsuario),
                    'numero_cuota': str(cuota.numero_cuota)
                }
            )
            
            # Guardar checkout_session_id
            cuota.stripe_checkout_session_id = checkout_session.id
            cuota.save()
            
            return True, {
                'url': checkout_session.url,
                'session_id': checkout_session.id,
                'monto': cuota.monto,
                'cuota': CuotaSerializer(cuota).data
            }, status.HTTP_200_OK
            
        except stripe.error.StripeError as e:
            return False, {"error": f"Error de Stripe: {str(e)}"}, status.HTTP_400_BAD_REQUEST
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def marcar_cuota_pagada(cuota):
        """Marca una cuota como pagada"""
        try:
            if cuota.pagada:
                return False, {"error": "La cuota ya está pagada"}, status.HTTP_400_BAD_REQUEST
            
            cuota.pagada = True
            cuota.fecha_pago = timezone.now().date()
            cuota.save()
            
            return True, {
                "mensaje": "Cuota marcada como pagada",
                "cuota": CuotaSerializer(cuota).data
            }, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
