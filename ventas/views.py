from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .services import VentaService
from .models import Pedido, PedidoItem

class PedidoListCreateView(APIView):
    # exigir autenticación para acceder a pedidos
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # request.user está garantizado como usuario autenticado por IsAuthenticated
        user = request.user
        if getattr(user, 'is_staff', False) or getattr(getattr(user, 'rol', None), 'nombre', None) in ['SuperAdmin','Trabajador','Vendedor']:
            qs = Pedido.objects.all().order_by('-fecha_creacion')
        else:
            qs = Pedido.objects.filter(cliente=user).order_by('-fecha_creacion')

        data = []
        for p in qs:
            data.append({
                "idPedido": p.idPedido,
                "total": str(p.total),
                "metodo_pago": p.metodo_pago,
                "estado": p.estado,
                "fecha_creacion": p.fecha_creacion,
                "items_count": p.items.count()
            })
        return Response(data)

    def post(self, request):
        payload = request.data or {}
        items = payload.get('items', [])
        if not items:
            return Response({"error": "Debe incluir al menos un item"}, status=status.HTTP_400_BAD_REQUEST)
        total = payload.get('total')
        metodo_pago = payload.get('metodo_pago', 'efectivo')
        datos_cliente = payload.get('datos_cliente')
        recoger_hasta = payload.get('recoger_hasta')

        pedido = Pedido.objects.create(
            cliente=request.user if hasattr(request.user, 'idUsuario') else request.user,
            total=total or 0,
            metodo_pago=metodo_pago,
            datos_cliente=datos_cliente,
            recoger_hasta=recoger_hasta
        )
        # crear items; aceptamos product_id opcional (asignando producto_id) y snapshot de nombre/precio
        for it in items:
            product_id = it.get('producto_id')
            PedidoItem.objects.create(
                pedido=pedido,
                producto_id=product_id if product_id else None,
                nombre=it.get('nombre', '')[:255],
                cantidad=it.get('cantidad', 1),
                precio=it.get('precio', 0)
            )
        return Response({"idPedido": pedido.idPedido}, status=status.HTTP_201_CREATED)


class PedidoDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id_pedido):
        pedido = get_object_or_404(Pedido, idPedido=id_pedido)
        user = request.user
        rol_nombre = getattr(getattr(user, 'rol', None), 'nombre', None)
        if pedido.cliente and pedido.cliente != user and rol_nombre not in ['SuperAdmin','Trabajador','Vendedor']:
            return Response({'error': 'No autorizado'}, status=403)
        items = []
        for it in pedido.items.all():
            items.append({
                "idItem": it.idItem,
                "producto_id": getattr(it, 'producto_id', None),
                "nombre": it.nombre,
                "cantidad": it.cantidad,
                "precio": str(it.precio),
                "subtotal": str(it.subtotal())
            })
        data = {
            "idPedido": pedido.idPedido,
            "total": str(pedido.total),
            "metodo_pago": pedido.metodo_pago,
            "estado": pedido.estado,
            "datos_cliente": pedido.datos_cliente,
            "recoger_hasta": pedido.recoger_hasta,
            "fecha_creacion": pedido.fecha_creacion,
            "items": items
        }
        return Response(data)


class ConfirmarPedidoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id_pedido):
        try:
            ok, result = VentaService.confirmar_pedido(id_pedido, usuario_vendedor=request.user, pago_info=request.data.get('pago'))
            if not ok:
                return Response({"error": str(result)}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"venta_id": result.idVenta}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class VentasReportesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Obtener métricas de ventas por período
        Query params: periodo (dia|semana|mes|trimestre|año), fecha_inicio, fecha_fin
        """
        periodo = request.query_params.get('periodo', 'mes')
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        
        # Calcular fechas según período si no se especifican
        if not fecha_inicio or not fecha_fin:
            fecha_fin = timezone.now().date()
            if periodo == 'dia':
                fecha_inicio = fecha_fin
            elif periodo == 'semana':
                fecha_inicio = fecha_fin - timedelta(days=7)
            elif periodo == 'mes':
                fecha_inicio = fecha_fin - timedelta(days=30)
            elif periodo == 'trimestre':
                fecha_inicio = fecha_fin - timedelta(days=90)
            elif periodo == 'año':
                fecha_inicio = fecha_fin - timedelta(days=365)
            else:
                fecha_inicio = fecha_fin - timedelta(days=30)

        # Filtrar ventas por período
        ventas_qs = Venta.objects.filter(
            fecha__date__gte=fecha_inicio,
            fecha__date__lte=fecha_fin
        )

        # Calcular métricas
        total_ventas = ventas_qs.aggregate(
            total=Sum('total'),
            cantidad=Count('idVenta')
        )

        # Ventas por día (para gráficos)
        ventas_por_dia = ventas_qs.extra(
            select={'dia': 'DATE(fecha)'}
        ).values('dia').annotate(
            total_dia=Sum('total'),
            cantidad_dia=Count('idVenta')
        ).order_by('dia')

        # Top productos más vendidos
        from .models import VentaItem
        productos_top = VentaItem.objects.filter(
            venta__fecha__date__gte=fecha_inicio,
            venta__fecha__date__lte=fecha_fin
        ).values('nombre').annotate(
            total_vendido=Sum('cantidad'),
            ingresos=Sum('precio_unitario')
        ).order_by('-total_vendido')[:10]

        return Response({
            'periodo': {
                'tipo': periodo,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin
            },
            'metricas': {
                'total_ingresos': total_ventas['total'] or 0,
                'total_ventas': total_ventas['cantidad'] or 0,
                'promedio_venta': (total_ventas['total'] or 0) / max(total_ventas['cantidad'] or 1, 1),
            },
            'ventas_por_dia': list(ventas_por_dia),
            'productos_top': list(productos_top)
        })

class VentasComparacionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Comparar ventas entre dos períodos
        Query params: periodo_actual_inicio, periodo_actual_fin, periodo_anterior_inicio, periodo_anterior_fin
        """
        # Período actual
        actual_inicio = request.query_params.get('periodo_actual_inicio')
        actual_fin = request.query_params.get('periodo_actual_fin')
        
        # Período anterior
        anterior_inicio = request.query_params.get('periodo_anterior_inicio')
        anterior_fin = request.query_params.get('periodo_anterior_fin')
        
        if not all([actual_inicio, actual_fin, anterior_inicio, anterior_fin]):
            return Response({'error': 'Faltan parámetros de fecha'}, status=400)
        
        # Ventas período actual
        ventas_actual = Venta.objects.filter(
            fecha__date__gte=actual_inicio,
            fecha__date__lte=actual_fin
        ).aggregate(
            total=Sum('total'),
            cantidad=Count('idVenta')
        )
        
        # Ventas período anterior
        ventas_anterior = Venta.objects.filter(
            fecha__date__gte=anterior_inicio,
            fecha__date__lte=anterior_fin
        ).aggregate(
            total=Sum('total'),
            cantidad=Count('idVenta')
        )
        
        # Calcular crecimiento
        crecimiento_ingresos = 0
        crecimiento_cantidad = 0
        
        if ventas_anterior['total'] and ventas_anterior['total'] > 0:
            crecimiento_ingresos = ((ventas_actual['total'] or 0) - ventas_anterior['total']) / ventas_anterior['total'] * 100
            
        if ventas_anterior['cantidad'] and ventas_anterior['cantidad'] > 0:
            crecimiento_cantidad = ((ventas_actual['cantidad'] or 0) - ventas_anterior['cantidad']) / ventas_anterior['cantidad'] * 100
        
        return Response({
            'periodo_actual': {
                'ingresos': ventas_actual['total'] or 0,
                'ventas': ventas_actual['cantidad'] or 0
            },
            'periodo_anterior': {
                'ingresos': ventas_anterior['total'] or 0,
                'ventas': ventas_anterior['cantidad'] or 0
            },
            'crecimiento': {
                'ingresos_porcentaje': round(crecimiento_ingresos, 2),
                'ventas_porcentaje': round(crecimiento_cantidad, 2)
            }
        })
