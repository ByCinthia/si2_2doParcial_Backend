from django.urls import path
from .views import PedidoListCreateView, PedidoDetailView, ConfirmarPedidoView, VentasReportesView, VentasComparacionView

app_name = 'ventas'

urlpatterns = [
    path('pedidos/', PedidoListCreateView.as_view(), name='pedido-list-create'),
    path('pedidos/<int:id_pedido>/', PedidoDetailView.as_view(), name='pedido-detail'),
    path('pedidos/<int:id_pedido>/confirmar/', ConfirmarPedidoView.as_view(), name='pedido-confirmar'),
    path('reportes/', VentasReportesView.as_view(), name='ventas-reportes'),
    path('comparacion/', VentasComparacionView.as_view(), name='ventas-comparacion'),
]