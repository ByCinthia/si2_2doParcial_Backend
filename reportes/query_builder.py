"""
Constructor de consultas Django ORM basado en parámetros parseados.
Genera QuerySets dinámicos para diferentes módulos del sistema.
"""
import logging
from django.db.models import Q, Count, Sum, Avg, Max, Min
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone

# Importar modelos del proyecto
from productos.models import Product, ProductVariant, InventoryMovement
from categorias.models import Categoria
from usuarios.models import Usuario, Rol

logger = logging.getLogger(__name__)


class QueryBuilder:
    """Constructor de consultas dinámicas para reportes."""
    
    def __init__(self):
        self.supported_modules = {
            'productos': self._build_products_query,
            'categorias': self._build_categories_query,
            'usuarios': self._build_users_query,
            'ventas': self._build_sales_query,
        }
    
    def build_query(self, params: dict) -> tuple:
        """
        Construye una consulta basada en los parámetros parseados.
        
        Args:
            params: Diccionario con parámetros del reporte
            
        Returns:
            tuple: (queryset, headers) donde:
                - queryset: QuerySet de Django con los datos
                - headers: Lista de nombres de columnas
        """
        module = params.get('module')
        if not module:
            raise ValueError("Módulo no especificado")
        
        if module not in self.supported_modules:
            raise ValueError(f"Módulo '{module}' no soportado. Disponibles: {list(self.supported_modules.keys())}")
        
        logger.info(f"Construyendo query para módulo: {module}")
        
        try:
            builder_func = self.supported_modules[module]
            queryset, headers = builder_func(params)
            
            logger.info(f"Query construido exitosamente. Módulo: {module}, Headers: {headers}")
            return queryset, headers
            
        except Exception as e:
            logger.error(f"Error construyendo query para {module}: {e}")
            raise
    
    def _build_products_query(self, params: dict) -> tuple:
        """Construye consulta para productos."""
        filters = params.get('filters', {})
        date_range = params.get('date_range', {})
        group_by = params.get('group_by')
        
        # Construir filtros base usando Q objects
        from django.db.models import Q
        base_filters = Q()
        
        # Filtros de fecha
        if date_range.get('start_date') and date_range.get('end_date'):
            base_filters &= Q(created_at__range=[date_range['start_date'], date_range['end_date']])
        
        # Filtros específicos  
        if filters.get('categoria'):
            base_filters &= Q(categoria__nombre__icontains=filters['categoria'])
        
        if filters.get('nombre'):
            base_filters &= Q(name__icontains=filters['nombre'])
        
        # Filtros de precio
        if filters.get('precio_min'):
            base_filters &= Q(base_price__gte=filters['precio_min'])
        
        if filters.get('precio_max'):
            base_filters &= Q(base_price__lte=filters['precio_max'])
            
        if filters.get('precio_exacto'):
            base_filters &= Q(base_price=filters['precio_exacto'])
        
        if 'activo' in filters:
            base_filters &= Q(active=filters['activo'])
        
        # Verificar si hay filtros de stock
        has_stock_filters = any(key in filters for key in ['stock_min', 'stock_max', 'stock_exacto'])
        
        if has_stock_filters:
            # Si hay filtros de stock, trabajar directamente con ProductVariant
            queryset = ProductVariant.objects.select_related('product', 'product__categoria')
            
            # Aplicar filtros base a través del producto
            queryset = queryset.filter(
                Q(product__created_at__range=[date_range['start_date'], date_range['end_date']]) if date_range.get('start_date') and date_range.get('end_date') else Q(),
                Q(product__categoria__nombre__icontains=filters['categoria']) if filters.get('categoria') else Q(),
                Q(product__name__icontains=filters['nombre']) if filters.get('nombre') else Q(),
                Q(product__base_price__gte=filters['precio_min']) if filters.get('precio_min') else Q(),
                Q(product__base_price__lte=filters['precio_max']) if filters.get('precio_max') else Q(),
                Q(product__base_price=filters['precio_exacto']) if filters.get('precio_exacto') else Q(),
                Q(product__active=filters['activo']) if 'activo' in filters else Q()
            )
            
            # Aplicar filtros de stock
            if filters.get('stock_min'):
                queryset = queryset.filter(stock__gte=filters['stock_min'])
                
            if filters.get('stock_max'):
                queryset = queryset.filter(stock__lte=filters['stock_max'])
                
            if filters.get('stock_exacto'):
                queryset = queryset.filter(stock=filters['stock_exacto'])
        else:
            # Sin filtros de stock, usar Product normal
            queryset = Product.objects.select_related('categoria').filter(base_filters)
        
        # Aplicar agrupación
        if group_by == 'categoria':
            if has_stock_filters:
                # Agrupar variantes por categoría de producto
                queryset = queryset.values('product__categoria__nombre').annotate(
                    total_variantes=Count('id'),
                    stock_total=Sum('stock'),
                    precio_promedio=Avg('price')
                ).order_by('product__categoria__nombre')
                headers = ['Categoría', 'Total Variantes', 'Stock Total', 'Precio Promedio']
            else:
                # Agrupar productos por categoría
                queryset = queryset.values('categoria__nombre').annotate(
                    total_productos=Count('id'),
                    precio_promedio=Avg('base_price'),
                    precio_min=Min('base_price'),
                    precio_max=Max('base_price')
                ).order_by('categoria__nombre')
                headers = ['Categoría', 'Total Productos', 'Precio Promedio', 'Precio Mínimo', 'Precio Máximo']
            
        elif group_by == 'mes':
            if has_stock_filters:
                queryset = queryset.annotate(
                    mes=TruncMonth('product__created_at')
                ).values('mes').annotate(
                    total_variantes=Count('id'),
                    stock_total=Sum('stock')
                ).order_by('mes')
                headers = ['Mes', 'Total Variantes', 'Stock Total']
            else:
                queryset = queryset.annotate(
                    mes=TruncMonth('created_at')
                ).values('mes').annotate(
                    total_productos=Count('id'),
                    precio_promedio=Avg('base_price')
                ).order_by('mes')
                headers = ['Mes', 'Total Productos', 'Precio Promedio']
            
        else:
            # Reporte detallado
            if has_stock_filters:
                # Mostrar información de variantes con stock
                queryset = queryset.values(
                    'product__id', 'product__name', 'sku', 'size', 'color', 
                    'price', 'stock', 'product__categoria__nombre', 'product__active'
                ).order_by('-product__created_at')
                headers = ['ID Producto', 'Producto', 'SKU', 'Talla', 'Color', 'Precio', 'Stock', 'Categoría', 'Activo']
            else:
                # Mostrar información de productos
                queryset = queryset.values(
                    'id', 'name', 'description', 'base_price', 
                    'categoria__nombre', 'active', 'created_at'
                ).order_by('-created_at')
                headers = ['ID', 'Nombre', 'Descripción', 'Precio Base', 'Categoría', 'Activo', 'Fecha Creación']
        
        # Limitar resultados para rendimiento
        queryset = queryset[:5000]
        
        return queryset, headers
    
    def _build_categories_query(self, params: dict) -> tuple:
        """Construye consulta para categorías."""
        queryset = Categoria.objects.all()
        filters = params.get('filters', {})
        date_range = params.get('date_range', {})
        
        # Aplicar filtros de fecha
        if date_range.get('start_date') and date_range.get('end_date'):
            queryset = queryset.filter(
                fecha_creacion__range=[date_range['start_date'], date_range['end_date']]
            )
        
        # Aplicar filtros específicos
        if filters.get('nombre'):
            queryset = queryset.filter(nombre__icontains=filters['nombre'])
        
        if 'activo' in filters:
            queryset = queryset.filter(activo=filters['activo'])
        
        # Agregar conteo de productos por categoría
        queryset = queryset.annotate(
            total_productos=Count('product'),
            productos_activos=Count('product', filter=Q(product__active=True))
        ).values(
            'idCategoria', 'nombre', 'descripcion', 'activo',
            'total_productos', 'productos_activos', 'fecha_creacion'
        ).order_by('nombre')
        
        headers = ['ID', 'Nombre', 'Descripción', 'Activo', 'Total Productos', 'Productos Activos', 'Fecha Creación']
        
        return queryset[:1000], headers
    
    def _build_users_query(self, params: dict) -> tuple:
        """Construye consulta para usuarios."""
        queryset = Usuario.objects.select_related('rol')
        filters = params.get('filters', {})
        date_range = params.get('date_range', {})
        group_by = params.get('group_by')
        
        # Aplicar filtros de fecha
        if date_range.get('start_date') and date_range.get('end_date'):
            queryset = queryset.filter(
                fecha_creacion__range=[date_range['start_date'], date_range['end_date']]
            )
        
        # Aplicar filtros específicos
        if filters.get('nombre'):
            queryset = queryset.filter(
                Q(username__icontains=filters['nombre']) | 
                Q(email__icontains=filters['nombre'])
            )
        
        if 'activo' in filters:
            queryset = queryset.filter(activo=filters['activo'])
        
        # Aplicar agrupación
        if group_by == 'rol' or group_by == 'usuario':
            queryset = queryset.values('rol__nombre').annotate(
                total_usuarios=Count('idUsuario'),
                usuarios_activos=Count('idUsuario', filter=Q(activo=True))
            ).order_by('rol__nombre')
            headers = ['Rol', 'Total Usuarios', 'Usuarios Activos']
            
        else:
            # Reporte detallado
            queryset = queryset.values(
                'idUsuario', 'username', 'email', 'telefono',
                'rol__nombre', 'activo', 'fecha_creacion'
            ).order_by('-fecha_creacion')
            headers = ['ID', 'Username', 'Email', 'Teléfono', 'Rol', 'Activo', 'Fecha Registro']
        
        return queryset[:5000], headers
    
    def _build_sales_query(self, params: dict) -> tuple:
        """Construye consulta para ventas."""
        # Nota: En este proyecto, el módulo ventas está vacío
        # Esta función es un placeholder para cuando se implementen las ventas
        logger.warning("Módulo de ventas no implementado en el proyecto actual")
        
        # Devolver datos de ejemplo o error
        return Product.objects.none(), ['Nota: Módulo ventas no disponible']
    
    def _build_inventory_query(self, params: dict) -> tuple:
        """Construye consulta para movimientos de inventario."""
        queryset = InventoryMovement.objects.select_related('variant__product')
        filters = params.get('filters', {})
        date_range = params.get('date_range', {})
        
        # Aplicar filtros de fecha
        if date_range.get('start_date') and date_range.get('end_date'):
            queryset = queryset.filter(
                created_at__range=[date_range['start_date'], date_range['end_date']]
            )
        
        # Filtros específicos
        if filters.get('tipo_movimiento'):
            queryset = queryset.filter(movement_type__icontains=filters['tipo_movimiento'])
        
        queryset = queryset.values(
            'variant__product__name', 'variant__sku', 'movement_type',
            'quantity', 'reason', 'created_at'
        ).order_by('-created_at')
        
        headers = ['Producto', 'SKU', 'Tipo Movimiento', 'Cantidad', 'Razón', 'Fecha']
        
        return queryset[:2000], headers


def build_report_query(params: dict) -> tuple:
    """
    Función de conveniencia para construir consultas de reportes.
    
    Args:
        params: Parámetros parseados del prompt
        
    Returns:
        tuple: (queryset, headers)
    """
    builder = QueryBuilder()
    return builder.build_query(params)