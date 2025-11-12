from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
from .services.service_metodo_pago import MetodoPagoService
from .services.service_venta import VentaService
from .services.service_cuota import CuotaService
from .models import Cuota
from .permissions import IsAdminUser, IsClienteUser
import stripe
import json


# ==================== MÉTODOS DE PAGO ====================

class MetodoPagoListView(APIView):
    """
    GET /api/ventas/metodos-pago/ - Lista todos los métodos de pago
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        success, result, status_code = MetodoPagoService.listar_metodos_pago()
        return Response(result, status=status_code)


class MetodoPagoDetailView(APIView):
    """
    GET /api/ventas/metodos-pago/{id}/ - Obtiene un método de pago
    """
    permission_classes = [AllowAny]
    
    def get(self, request, id_metodo):
        success, result, status_code = MetodoPagoService.obtener_metodo_pago(id_metodo)
        return Response(result, status=status_code)


# ==================== VENTAS ====================

class VentaListCreateView(APIView):
    """
    GET /api/ventas/ - Lista todas las ventas (solo las del usuario autenticado)
    POST /api/ventas/ - Crea venta (flujo depende del número de cuotas)
    
    Flujos:
    - nrocuotas = 1: Genera Stripe Checkout → pago inmediato → venta creada por webhook
    - nrocuotas > 1: Crea venta inmediatamente con cuotas → pagar cuotas individualmente después
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Listar solo ventas del usuario autenticado
        success, result, status_code = VentaService.listar_ventas_usuario(request.user)
        return Response(result, status=status_code)
    
    def post(self, request):
        nrocuotas = request.data.get('nrocuotas', 1)
        
        # PAGO AL CONTADO (1 cuota) - Usar Stripe Checkout
        if nrocuotas == 1:
            success, result, status_code = VentaService.crear_checkout_session_contado(
                request.data, request.user
            )
            return Response(result, status=status_code)
        
        # PAGO EN CUOTAS (3, 6 o 12) - Crear venta inmediatamente
        else:
            success, result, status_code = VentaService.crear_venta_con_cuotas(
                request.data, request.user
            )
            return Response(result, status=status_code)


class VentaDetailView(APIView):
    """
    GET /api/ventas/{id}/ - Obtiene una venta con sus detalles y cuotas
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_venta):
        success, result, status_code = VentaService.obtener_venta(id_venta)
        return Response(result, status=status_code)


class MisVentasView(APIView):
    """
    GET /api/ventas/mis-ventas/ - Lista todas las ventas del usuario autenticado
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        success, result, status_code = VentaService.listar_ventas_usuario(request.user)
        return Response(result, status=status_code)


# ==================== CUOTAS ====================

class CuotasVentaListView(APIView):
    """
    GET /api/ventas/{id_venta}/cuotas/ - Lista cuotas de una venta
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_venta):
        success, result, status_code = CuotaService.listar_cuotas_venta(id_venta)
        return Response(result, status=status_code)


class MisCuotasView(APIView):
    """
    GET /api/ventas/mis-cuotas/ - Lista todas las cuotas del usuario
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        success, result, status_code = CuotaService.listar_cuotas_usuario(request.user)
        return Response(result, status=status_code)


class MisCuotasPendientesView(APIView):
    """
    GET /api/ventas/mis-cuotas/pendientes/ - Lista cuotas pendientes del usuario
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        success, result, status_code = CuotaService.listar_cuotas_pendientes_usuario(request.user)
        return Response(result, status=status_code)


class CuotaDetailView(APIView):
    """
    GET /api/ventas/cuotas/{id}/ - Obtiene una cuota por ID
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_cuota):
        success, result, status_code = CuotaService.obtener_cuota(id_cuota)
        return Response(result, status=status_code)


# ==================== PAGOS CON STRIPE ====================

class CuotaCrearPaymentIntentView(APIView):
    """
    POST /api/ventas/cuotas/{id}/crear-payment-intent/
    Crea un Payment Intent para pagar DENTRO de Flutter con flutter_stripe
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, id_cuota):
        try:
            cuota = Cuota.objects.select_related('venta__usuario').get(idCuota=id_cuota)
            
            # Verificar que la cuota pertenece al usuario
            if cuota.venta.usuario.idUsuario != request.user.idUsuario:
                return Response({'error': 'No autorizado'}, status=403)
            
            # Verificar que no esté pagada
            if cuota.pagada:
                return Response({'error': 'Cuota ya pagada'}, status=400)
            
            # Crear Payment Intent
            success, result, status_code = CuotaService.crear_payment_intent_cuota(cuota)
            return Response(result, status=status_code)
            
        except Cuota.DoesNotExist:
            return Response({'error': 'Cuota no encontrada'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


class CuotaGenerarLinkPagoView(APIView):
    """
    POST /api/ventas/cuotas/{id}/generar-link-pago/
    Genera un link de pago (Hosted Checkout) para pagar en NAVEGADOR
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, id_cuota):
        try:
            cuota = Cuota.objects.select_related('venta__usuario').get(idCuota=id_cuota)
            
            # Verificar que la cuota pertenece al usuario
            if cuota.venta.usuario.idUsuario != request.user.idUsuario:
                return Response({'error': 'No autorizado'}, status=403)
            
            # Verificar que no esté pagada
            if cuota.pagada:
                return Response({'error': 'Cuota ya pagada'}, status=400)
            
            # Generar link de pago
            success, result, status_code = CuotaService.generar_link_pago_cuota(cuota)
            return Response(result, status=status_code)
            
        except Cuota.DoesNotExist:
            return Response({'error': 'Cuota no encontrada'}, status=404)
        except Exception as e:
            return Response({'error': str(e)}, status=500)


# ==================== WEBHOOK STRIPE ====================

@csrf_exempt
def stripe_webhook(request):
    """
    POST /api/ventas/webhook/stripe/
    Webhook de Stripe para confirmar pagos automáticamente.
    Maneja eventos de:
    - payment_intent.succeeded (pago dentro de Flutter)
    - checkout.session.completed (pago con link externo Web)
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    # Configurar Stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        # Verificar firma del webhook
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Payload inválido
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Firma inválida
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(status=400)
    
    # Manejar el evento
    event_type = event['type']
    
    # ==================== PAYMENT INTENT (FLUTTER) ====================
    if event_type == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        
        # Obtener metadata
        cuota_id = payment_intent['metadata'].get('cuota_id')
        
        if cuota_id:
            try:
                cuota = Cuota.objects.get(idCuota=cuota_id)
                
                # Marcar cuota como pagada
                if not cuota.pagada:
                    cuota.pagada = True
                    cuota.fecha_pago = timezone.now().date()
                    cuota.stripe_payment_intent_id = payment_intent['id']
                    cuota.save()
                    
                    print(f"✅ Cuota {cuota_id} pagada exitosamente (Payment Intent)")
            except Cuota.DoesNotExist:
                print(f"❌ Cuota {cuota_id} no encontrada")
    
    # ==================== CHECKOUT SESSION (WEB) ====================
    elif event_type == 'checkout.session.completed':
        checkout_session = event['data']['object']
        
        # Obtener metadata
        tipo = checkout_session['metadata'].get('tipo')
        
        # Si es VENTA AL CONTADO (1 cuota), crear la venta
        if tipo == 'venta_contado':
            success, venta = VentaService.crear_venta_desde_webhook(checkout_session)
            if success:
                print(f"✅ Venta al contado creada desde webhook: ID {venta.idVenta}")
            else:
                print(f"❌ Error creando venta al contado desde webhook")
        
        # Si es pago de CUOTA INDIVIDUAL, marcar como pagada
        else:
            cuota_id = checkout_session['metadata'].get('cuota_id')
            
            if cuota_id:
                try:
                    cuota = Cuota.objects.get(idCuota=cuota_id)
                    
                    # Marcar cuota como pagada
                    if not cuota.pagada:
                        cuota.pagada = True
                        cuota.fecha_pago = timezone.now().date()
                        cuota.stripe_checkout_session_id = checkout_session['id']
                        cuota.save()
                        
                        print(f"✅ Cuota {cuota_id} pagada exitosamente (Checkout Session)")
                except Cuota.DoesNotExist:
                    print(f"❌ Cuota {cuota_id} no encontrada")
    
    # ==================== PAYMENT INTENT FAILED ====================
    elif event_type == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        cuota_id = payment_intent['metadata'].get('cuota_id')
        
        if cuota_id:
            print(f"❌ Pago fallido para cuota {cuota_id}")
            # Aquí podrías enviar una notificación al usuario
    
    # Retornar 200 a Stripe
    return HttpResponse(status=200)


# ==================== ADMIN - VENTAS ====================

class AdminVentasListView(APIView):
    """
    GET /api/ventas/admin/ventas/ - Lista todas las ventas del sistema
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        success, result, status_code = VentaService.listar_ventas()
        return Response(result, status=status_code)


class AdminVentaDetailView(APIView):
    """
    GET /api/ventas/admin/ventas/{id}/ - Obtiene detalles de una venta
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request, id_venta):
        success, result, status_code = VentaService.obtener_venta(id_venta)
        return Response(result, status=status_code)


class AdminEstadisticasVentasView(APIView):
    """
    GET /api/ventas/admin/ventas/estadisticas/ - Obtiene estadísticas de ventas
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        success, result, status_code = VentaService.obtener_estadisticas_ventas()
        return Response(result, status=status_code)


# ==================== ADMIN - CUOTAS ====================

class AdminCuotasListView(APIView):
    """
    GET /api/ventas/admin/cuotas/ - Lista todas las cuotas del sistema
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        success, result, status_code = CuotaService.listar_todas_cuotas()
        return Response(result, status=status_code)


class AdminCuotasPendientesView(APIView):
    """
    GET /api/ventas/admin/cuotas/pendientes/ - Lista todas las cuotas pendientes
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        success, result, status_code = CuotaService.listar_cuotas_pendientes()
        return Response(result, status=status_code)


class AdminCuotasVencidasView(APIView):
    """
    GET /api/ventas/admin/cuotas/vencidas/ - Lista todas las cuotas vencidas
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        success, result, status_code = CuotaService.listar_cuotas_vencidas()
        return Response(result, status=status_code)


class AdminCuotaDetailView(APIView):
    """
    GET /api/ventas/admin/cuotas/{id}/ - Obtiene detalles de una cuota
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request, id_cuota):
        success, result, status_code = CuotaService.obtener_cuota(id_cuota)
        return Response(result, status=status_code)


class AdminEstadisticasCuotasView(APIView):
    """
    GET /api/ventas/admin/cuotas/estadisticas/ - Obtiene estadísticas de cuotas
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        success, result, status_code = CuotaService.obtener_estadisticas_cuotas()
        return Response(result, status=status_code)
