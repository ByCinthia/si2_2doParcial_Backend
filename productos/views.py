from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from usuarios.permissions import CanManageUsers
import logging
import json
from rest_framework.decorators import action, api_view, permission_classes
from django.db import transaction
from django.db.models import Q

from .services.services_producto import ProductoService
from .serializers import ProductListSerializer, ProductDetailSerializer, ProductVariantSerializer, ProductSerializer
from .models import Product, ProductVariant, ProductImage
from .serializers_inventory import ProductImageSerializer
from categorias.models import Categoria
from ventas.models import MovimientoInventario

logger = logging.getLogger(__name__)


class ProductoListCreateView(APIView):
    """Listar y crear productos"""

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        try:
            success, data, status_code = ProductoService.listar_productos()
            return Response(data, status=status_code)
        except Exception as e:
            # queda en logs completos en la consola de runserver
            logger.exception("Error al listar productos (GET /api/productos/)")
            return Response(
                {"error": "Error interno al listar productos. Revisa logs en el servidor."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        try:
            # ✅ CORRECTO: usar data=request.data
            serializer = ProductSerializer(data=request.data)
            
            if serializer.is_valid():
                product = serializer.save()
                return Response(
                    ProductSerializer(product).data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProductoDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        success, data, status_code = ProductoService.obtener_producto(pk)
        return Response(data, status=status_code)

    def put(self, request, pk):
        success, data, status_code = ProductoService.actualizar_producto(pk, request.data)
        return Response(data, status=status_code)

    def patch(self, request, pk):
        success, data, status_code = ProductoService.actualizar_producto(pk, request.data)
        return Response(data, status=status_code)

    def delete(self, request, pk):
        success, data, status_code = ProductoService.eliminar_producto(pk)
        return Response(data, status=status_code)


class ProductoInventoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        success, data, status_code = ProductoService.listar_inventario(pk)
        return Response(data, status=status_code)


class VariantStockUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, variant_id):
        variant = get_object_or_404(ProductVariant, pk=variant_id)
        serializer = ProductVariantSerializer(variant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InventarioListView(APIView):
    """Lista todas las variantes agrupadas por producto (inventario global)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        GET /api/productos/inventario/
        
        Query params opcionales:
        - categoria: filtrar por ID de categoría
        - search: buscar por nombre de producto
        - low_stock: true para ver solo stock bajo
        - out_of_stock: true para ver solo sin stock
        """
        from .serializers import InventoryVariantSerializer
        
        # Filtros
        categoria_id = request.query_params.get('categoria')
        search = request.query_params.get('search')
        low_stock = request.query_params.get('low_stock', '').lower() == 'true'
        out_of_stock = request.query_params.get('out_of_stock', '').lower() == 'true'
        
        # Query base
        variants = ProductVariant.objects.select_related(
            'product', 
            'product__categoria'
        ).all()
        
        # Aplicar filtros
        if categoria_id:
            variants = variants.filter(product__categoria_id=categoria_id)
        
        if search:
            from django.db.models import Q
            variants = variants.filter(
                Q(product__name__icontains=search) |
                Q(size__icontains=search) |
                Q(color__icontains=search)
            )
        
        if low_stock:
            variants = variants.filter(stock__gt=0, stock__lt=5)
        
        if out_of_stock:
            variants = variants.filter(stock=0)
        
        # Serializar
        serializer = InventoryVariantSerializer(variants, many=True)
        
        # Agrupar por producto para el frontend
        data_agrupada = {}
        for variant_data in serializer.data:
            product_id = variant_data['product_id']
            
            if product_id not in data_agrupada:
                data_agrupada[product_id] = {
                    'product_id': product_id,
                    'product_name': variant_data['product_name'],
                    'categoria': variant_data['categoria'],
                    'total_stock': 0,
                    'variants': []
                }
            
            data_agrupada[product_id]['variants'].append(variant_data)
            data_agrupada[product_id]['total_stock'] += variant_data['stock']
        
        return Response({
            'count': len(data_agrupada),
            'results': list(data_agrupada.values())
        }, status=200)


class InventarioAjustarView(APIView):
    """Ajusta stock: body -> { "variant_id": int, "delta": int } o { "variant_id": int, "stock": int }
    Solo usuarios con permiso pueden ajustar inventario."""
    permission_classes = [CanManageUsers]

    def post(self, request):
        variant_id = request.data.get('variant_id')
        delta = request.data.get('delta')
        stock = request.data.get('stock')
        motivo = request.data.get('motivo')

        if not variant_id:
            return Response({"error": "variant_id requerido"}, status=400)

        success, data, status_code = ProductoService.ajustar_stock(variant_id, delta=delta, stock=stock, usuario=getattr(request, 'user', None), motivo=motivo)
        return Response(data, status=status_code)


class ProductImageUploadView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        """
        Espera multipart/form-data con:
        - product: id del producto
        - image: archivo de imagen
        - alt_text, is_main (opcional)
        """
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related('variants', 'images', 'categoria').all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info("=== INICIO CREATE PRODUCTO ===")
            logger.info(f"request.data: {request.data}")
            logger.info(f"request.FILES: {request.FILES}")
            logger.info(f"Content-Type: {request.content_type}")
            
            # Obtener y parsear variantes
            variants_raw = request.data.get('variants')
            logger.info(f"variants_raw recibido: {variants_raw} (tipo: {type(variants_raw)})")
            
            if not variants_raw:
                return Response(
                    {'error': 'Debe incluir al menos una variante'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parsear JSON si es string
            if isinstance(variants_raw, str):
                import json
                try:
                    variants_data = json.loads(variants_raw)
                    logger.info(f"variants_data parseado: {variants_data}")
                except json.JSONDecodeError as e:
                    logger.error(f"Error parseando variants: {e}")
                    return Response(
                        {'error': f'JSON de variantes inválido: {str(e)}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                variants_data = variants_raw
            
            # Crear diccionario con todos los datos
            data = {
                'name': request.data.get('name'),
                'description': request.data.get('description', ''),
                'cost_price': request.data.get('cost_price'),
                'price': request.data.get('price'),
                'categoria': request.data.get('categoria'),
                'active': request.data.get('active', 'true').lower() == 'true',
                'variants': variants_data
            }
            
            logger.info(f"Datos a serializar: {data}")
            
            # Serializar y validar
            serializer = self.get_serializer(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            
            logger.info("Serializer validado correctamente")
            
            # Guardar producto
            product = serializer.save()
            logger.info(f"Producto guardado: ID {product.id}")
            
            # Procesar imágenes
            files = request.FILES.getlist('images')
            logger.info(f"Procesando {len(files)} imágenes")
            
            for idx, file in enumerate(files):
                logger.info(f"Subiendo imagen {idx}: {file.name}")
                ProductImage.objects.create(
                    product=product,
                    image=file,
                    is_main=(idx == 0),
                    order=idx
                )
            
            logger.info("=== FIN CREATE PRODUCTO (ÉXITO) ===")
            
            # Retornar respuesta con producto completo
            return Response(
                ProductSerializer(product, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
            
        except serializers.ValidationError as e:
            logger.error(f"Error de validación: {e.detail}")
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error inesperado: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Error interno: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """Actualizar producto existente"""
        instance = self.get_object()
        
        print(f"\n🔄 UPDATE PRODUCTO ID: {instance.id}")
        
        # Actualizar campos básicos
        if 'name' in request.data:
            instance.name = str(request.data['name']).strip()
        if 'description' in request.data:
            instance.description = str(request.data['description']).strip()
        if 'price' in request.data:
            try:
                instance.price = float(request.data['price'])
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Precio inválido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if 'categoria' in request.data:
            try:
                categoria = Categoria.objects.get(id=int(request.data['categoria']))
                instance.categoria = categoria
            except Categoria.DoesNotExist:
                return Response(
                    {'error': f'Categoría ID {request.data["categoria"]} no existe'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if 'active' in request.data:
            instance.active = str(request.data['active']).lower() in ['true', '1', 'yes', 'on']
        
        instance.save()
        print(f"✅ Producto actualizado")
        
        # Actualizar variantes si vienen
        variants_raw = request.data.get('variants')
        if variants_raw:
            try:
                variants_data = json.loads(variants_raw) if isinstance(variants_raw, str) else variants_raw
                
                # Eliminar variantes antiguas
                deleted_count, _ = ProductVariant.objects.filter(product=instance).delete()
                print(f"🗑️ {deleted_count} variante(s) eliminada(s)")
                
                # Crear nuevas variantes
                for idx, v in enumerate(variants_data):
                    stock = max(0, int(v.get('stock', 2)))
                    variant_price = v.get('price')
                    if variant_price:
                        try:
                            variant_price = float(variant_price)
                        except (ValueError, TypeError):
                            variant_price = None
                    
                    # No gestionar SKU desde aquí
                    sku = None
                    
                    variant = ProductVariant.objects.create(
                        product=instance,
                        sku=sku,
                        size=v.get('size'),
                        color=v.get('color'),
                        model_name=v.get('model_name'),
                        price=variant_price,
                        stock=stock
                    )
                    print(f"✅ Variante creada: ID {variant.id} (Stock: {variant.stock})")
                    
            except Exception as e:
                print(f"❌ Error actualizando variantes: {str(e)}")
                return Response(
                    {'error': f'Error actualizando variantes: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Actualizar imágenes si vienen
        files = request.FILES.getlist('images')
        if files:
            ProductImage.objects.filter(product=instance).delete()
            for idx, f in enumerate(files):
                ProductImage.objects.create(
                    product=instance,
                    image=f,
                    is_main=(idx == 0),
                    order=idx
                )
            print(f"✅ {len(files)} imagen(es) actualizada(s)")
        
        instance.refresh_from_db()
        return Response(ProductDetailSerializer(instance).data)
    
    @action(detail=False, methods=['get'], url_path='inventory')
    def inventory(self, request):
        """Obtener inventario (variantes con stock)"""
        product_id = request.query_params.get('product')
        low_stock = request.query_params.get('low_stock', '').lower() == 'true'
        
        queryset = ProductVariant.objects.select_related('product', 'product__categoria').all()
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if low_stock:
            queryset = queryset.filter(stock__gt=0, stock__lt=5)
        
        data = []
        for variant in queryset:
            data.append({
                'id': variant.id,
                'product_id': variant.product.id,
                'product_name': variant.product.name,
                'categoria': {
                    'id': variant.product.categoria.id if variant.product.categoria else None,
                    'nombre': variant.product.categoria.nombre if variant.product.categoria else None
                },
                # sku removido
                'size': variant.size,
                'color': variant.color,
                'model_name': variant.model_name,
                'price': str(variant.price or variant.product.price),
                'stock': variant.stock,
                'is_available': variant.stock > 0,
                'is_low_stock': 0 < variant.stock < 5
            })
        
        return Response(data)


class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.select_related('product').all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['patch'], url_path='update-stock')
    def update_stock(self, request, pk=None):
        """
        Actualizar stock de una variante
        
        Body opciones:
        1. Reemplazar stock:
           {"stock": 15}
        
        2. Incrementar:
           {"action": "increase", "quantity": 10}
        
        3. Decrementar:
           {"action": "decrease", "quantity": 2}
        """
        variant = self.get_object()
        action_type = request.data.get('action')
        
        if action_type == 'increase':
            quantity = int(request.data.get('quantity', 0))
            if quantity <= 0:
                return Response(
                    {'error': 'La cantidad debe ser mayor a 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            variant.stock += quantity
            variant.save()
            return Response({
                'message': f'Stock incrementado en {quantity}',
                'variant': ProductVariantSerializer(variant).data
            })
        
        elif action_type == 'decrease':
            quantity = int(request.data.get('quantity', 0))
            if quantity <= 0:
                return Response(
                    {'error': 'La cantidad debe ser mayor a 0'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if quantity > variant.stock:
                return Response(
                    {'error': f'Stock insuficiente. Disponible: {variant.stock}, Solicitado: {quantity}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            variant.stock -= quantity
            variant.save()
            return Response({
                'message': f'Stock reducido en {quantity}',
                'variant': ProductVariantSerializer(variant).data
            })
        
        else:
            # Actualización directa
            new_stock = request.data.get('stock')
            if new_stock is None:
                return Response(
                    {'error': 'Debe proporcionar "stock" o "action" + "quantity"'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                new_stock = int(new_stock)
                if new_stock < 0:
                    return Response(
                        {'error': 'El stock no puede ser negativo'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Stock debe ser un número entero'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            variant.stock = new_stock
            variant.save()
            
            return Response({
                'message': 'Stock actualizado correctamente',
                'variant': ProductVariantSerializer(variant).data
            })
    
    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        """Obtener variantes con stock bajo (< 5)"""
        variants = ProductVariant.objects.filter(stock__gt=0, stock__lt=5).select_related('product')
        data = []
        for v in variants:
            data.append({
                'id': v.id,
                'product_id': v.product.id,
                'product_name': v.product.name,
                'size': v.size,
                'stock': v.stock,
                'is_available': True,
                'is_low_stock': True
            })
        return Response(data)
    
    @action(detail=False, methods=['get'], url_path='out-of-stock')
    def out_of_stock(self, request):
        """Obtener variantes sin stock"""
        variants = ProductVariant.objects.filter(stock=0).select_related('product')
        data = []
        for v in variants:
            data.append({
                'id': v.id,
                'product_id': v.product.id,
                'product_name': v.product.name,
                'size': v.size,
                'stock': 0,
                'is_available': False
            })
        return Response(data)


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.select_related('product').all()
    serializer_class = ProductImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['post'], url_path='upload')
    def upload_image(self, request):
        """
        Subir imagen a un producto existente
        
        Form-data:
        - product: integer (ID del producto)
        - image: file
        - alt_text: string (opcional)
        - is_main: boolean (opcional)
        """
        product_id = request.data.get('product')
        if not product_id:
            return Response(
                {'error': 'Debe especificar el ID del producto (campo "product")'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=int(product_id))
        except Product.DoesNotExist:
            return Response(
                {'error': f'Producto con ID {product_id} no existe'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except (ValueError, TypeError):
            return Response(
                {'error': 'ID de producto inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {'error': 'Debe incluir el archivo de imagen (campo "image")'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar tamaño
        if image_file.size > 5 * 1024 * 1024:
            return Response(
                {'error': 'La imagen debe ser menor a 5MB'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear imagen
        is_main = str(request.data.get('is_main', 'false')).lower() in ['true', '1', 'yes']
        order = ProductImage.objects.filter(product=product).count()
        
        image = ProductImage.objects.create(
            product=product,
            image=image_file,
            alt_text=request.data.get('alt_text'),
            is_main=is_main,
            order=order
        )
        
        return Response(
            ProductImageSerializer(image).data,
            status=status.HTTP_201_CREATED
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_list(request):
    """
    Listado de inventario con filtros
    """
    queryset = ProductVariant.objects.select_related('product', 'product__categoria').all()
    
    # Filtros opcionales
    search = request.GET.get('search', '')
    categoria = request.GET.get('categoria', '')
    stock_bajo = request.GET.get('stock_bajo', '')
    
    if search:
        queryset = queryset.filter(
            Q(product__name__icontains=search) |
            Q(sku__icontains=search) |
            Q(size__icontains=search) |
            Q(color__icontains=search)
        )
    
    if categoria:
        queryset = queryset.filter(product__categoria_id=categoria)
    
    if stock_bajo == 'true':
        queryset = queryset.filter(stock__lt=5, stock__gt=0)
    
    # Serializar datos
    data = []
    for variante in queryset:
        data.append({
            'id': variante.id,
            'producto': variante.product.name,
            'sku': variante.sku or '',
            'talla': variante.size or '',
            'color': variante.color or '',
            'stock': variante.stock,
            'precio_venta': str(variante.get_sale_price()),
            'precio_costo': str(variante.get_cost_price()),
            'categoria': variante.product.categoria.nombre if variante.product.categoria else '',
            'is_low_stock': variante.is_low_stock,
            'is_available': variante.is_available
        })
    
    return Response(data)
