from django.urls import path
from .views import (
    # Métodos de Pago
    MetodoPagoListView,
    MetodoPagoDetailView,
    
    # Cliente - Ventas
    VentaListCreateView,
    VentaDetailView,
    MisVentasView,
    
    # Cliente - Cuotas
    CuotasVentaListView,
    MisCuotasView,
    MisCuotasPendientesView,
    CuotaDetailView,
    
    # Cliente - Pagos Stripe
    CuotaCrearPaymentIntentView,
    CuotaGenerarLinkPagoView,
    
    # Admin - Ventas
    AdminVentasListView,
    AdminVentaDetailView,
    AdminEstadisticasVentasView,
    
    # Admin - Cuotas
    AdminCuotasListView,
    AdminCuotasPendientesView,
    AdminCuotasVencidasView,
    AdminCuotaDetailView,
    AdminEstadisticasCuotasView,
    
    # Webhook
    stripe_webhook,
)

app_name = 'ventas'

urlpatterns = [
    # ==================== MÉTODOS DE PAGO (Público) ====================
    # GET /api/ventas/metodos-pago/ - Listar métodos de pago
    path('metodos-pago/', MetodoPagoListView.as_view(), name='metodos-pago-list'),
    
    # GET /api/ventas/metodos-pago/{id}/ - Obtener método de pago
    path('metodos-pago/<int:id_metodo>/', MetodoPagoDetailView.as_view(), name='metodos-pago-detail'),
    
    
    # ==================== CLIENTE - VENTAS ====================
    # POST /api/ventas/ - Crear nueva venta (Cliente)
    path('', VentaListCreateView.as_view(), name='venta-list-create'),
    
    # GET /api/ventas/mis-ventas/ - Listar mis ventas (Cliente)
    path('mis-ventas/', MisVentasView.as_view(), name='mis-ventas'),
    
    # GET /api/ventas/{id}/ - Obtener detalle de mi venta (Cliente)
    path('<int:id_venta>/', VentaDetailView.as_view(), name='venta-detail'),
    
    # GET /api/ventas/{id_venta}/cuotas/ - Listar cuotas de mi venta (Cliente)
    path('<int:id_venta>/cuotas/', CuotasVentaListView.as_view(), name='cuotas-venta-list'),
    
    
    # ==================== CLIENTE - CUOTAS ====================
    # GET /api/ventas/mis-cuotas/ - Listar todas mis cuotas (Cliente)
    path('mis-cuotas/', MisCuotasView.as_view(), name='mis-cuotas'),
    
    # GET /api/ventas/mis-cuotas/pendientes/ - Listar mis cuotas pendientes (Cliente)
    path('mis-cuotas/pendientes/', MisCuotasPendientesView.as_view(), name='mis-cuotas-pendientes'),
    
    # GET /api/ventas/cuotas/{id}/ - Obtener detalle de mi cuota (Cliente)
    path('cuotas/<int:id_cuota>/', CuotaDetailView.as_view(), name='cuota-detail'),
    
    
    # ==================== CLIENTE - PAGOS STRIPE ====================
    # POST /api/ventas/cuotas/{id}/crear-payment-intent/ - Pagar cuota con Flutter (Cliente)
    path('cuotas/<int:id_cuota>/crear-payment-intent/', 
         CuotaCrearPaymentIntentView.as_view(), 
         name='cuota-crear-payment-intent'),
    
    # POST /api/ventas/cuotas/{id}/generar-link-pago/ - Generar link de pago Web (Cliente)
    path('cuotas/<int:id_cuota>/generar-link-pago/', 
         CuotaGenerarLinkPagoView.as_view(), 
         name='cuota-generar-link-pago'),
    
    
    # ==================== ADMIN - VENTAS ====================
    # GET /api/ventas/admin/ventas/ - Listar todas las ventas del sistema (Admin)
    path('admin/ventas/', AdminVentasListView.as_view(), name='admin-ventas-list'),
    
    # GET /api/ventas/admin/ventas/{id}/ - Obtener detalle de cualquier venta (Admin)
    path('admin/ventas/<int:id_venta>/', AdminVentaDetailView.as_view(), name='admin-venta-detail'),
    
    # GET /api/ventas/admin/estadisticas/ventas/ - Estadísticas de ventas (Admin)
    path('admin/estadisticas/ventas/', AdminEstadisticasVentasView.as_view(), name='admin-estadisticas-ventas'),
    
    
    # ==================== ADMIN - CUOTAS ====================
    # GET /api/ventas/admin/cuotas/ - Listar todas las cuotas del sistema (Admin)
    path('admin/cuotas/', AdminCuotasListView.as_view(), name='admin-cuotas-list'),
    
    # GET /api/ventas/admin/cuotas/pendientes/ - Listar todas las cuotas pendientes (Admin)
    path('admin/cuotas/pendientes/', AdminCuotasPendientesView.as_view(), name='admin-cuotas-pendientes'),
    
    # GET /api/ventas/admin/cuotas/vencidas/ - Listar todas las cuotas vencidas (Admin)
    path('admin/cuotas/vencidas/', AdminCuotasVencidasView.as_view(), name='admin-cuotas-vencidas'),
    
    # GET /api/ventas/admin/cuotas/{id}/ - Obtener detalle de cualquier cuota (Admin)
    path('admin/cuotas/<int:id_cuota>/', AdminCuotaDetailView.as_view(), name='admin-cuota-detail'),
    
    # GET /api/ventas/admin/estadisticas/cuotas/ - Estadísticas de cuotas (Admin)
    path('admin/estadisticas/cuotas/', AdminEstadisticasCuotasView.as_view(), name='admin-estadisticas-cuotas'),
    
    
    # ==================== WEBHOOK ====================
    # POST /api/ventas/webhook/stripe/ - Webhook de Stripe (sin autenticación)
    path('webhook/stripe/', stripe_webhook, name='stripe-webhook'),
]
