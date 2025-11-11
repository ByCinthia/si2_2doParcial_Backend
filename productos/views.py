from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from usuarios.permissions import CanManageUsers
import logging
import json
from rest_framework.decorators import action
from django.db import transaction

from .services.services_producto import ProductoService
from .serializers import ProductListSerializer, ProductDetailSerializer, ProductVariantSerializer
from .models import Product, ProductVariant, ProductImage
from .serializers_inventory import ProductImageSerializer
from categorias.models import Categoria

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
            # Pasar el objeto request entero al servicio para que pueda manejar form-data y files
            success, data, status_code = ProductoService.crear_producto(request)
            return Response(data, status=status_code)
        except Exception:
            logger.exception("Error creando producto")
            return Response({"error":"Error interno al crear producto"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return ProductListSerializer
        return ProductDetailSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Crear producto con variantes e imágenes
        
        Form-data esperado:
        - name: string (requerido)
        - description: string
        - price: decimal (requerido)
        - categoria: integer (requerido)
        - active: boolean (default: true)
        - variants: JSON string array (REQUERIDO - al menos 1 variante)
          Ejemplo: [{"size":"M","color":"Azul","stock":10}]
        - images: file[] (opcional, múltiples archivos)
        """
        print("\n" + "="*100)
        print("🔍 CREATE PRODUCTO - INICIO")
        print("="*100)
        print(f"📥 Request.data keys: {list(request.data.keys())}")
        print(f"📥 Request.FILES keys: {list(request.FILES.keys())}")
        
        # ========== VALIDAR DATOS BÁSICOS ==========
        errors = {}
        
        # Nombre
        name = request.data.get('name')
        if not name or not str(name).strip():
            errors['name'] = ['El nombre del producto es requerido']
        
        # Precio
        price = request.data.get('price')
        if not price:
            errors['price'] = ['El precio es requerido']
        else:
            try:
                price = float(price)
                if price <= 0:
                    errors['price'] = ['El precio debe ser mayor a 0']
            except (ValueError, TypeError):
                errors['price'] = ['Precio inválido']
        
        # Categoría
        categoria_id = request.data.get('categoria')
        if not categoria_id:
            errors['categoria'] = ['La categoría es requerida']
        else:
            try:
                categoria = Categoria.objects.get(id=int(categoria_id))
                print(f"✅ Categoría: {categoria.nombre} (ID: {categoria.id})")
            except Categoria.DoesNotExist:
                errors['categoria'] = [f'Categoría con ID {categoria_id} no existe']
            except (ValueError, TypeError):
                errors['categoria'] = ['ID de categoría inválido']
        
        # Variantes (CRÍTICO)
        variants_raw = request.data.get('variants')
        print(f"\n🔍 Variantes recibidas (raw): {repr(variants_raw)}")
        print(f"🔍 Tipo de variantes: {type(variants_raw)}")
        
        if not variants_raw:
            errors['variants'] = ['Debe incluir al menos una variante (size, color, stock)']
        else:
            # Intentar parsear variantes
            try:
                if isinstance(variants_raw, str):
                    # Si viene como string JSON
                    variants_data = json.loads(variants_raw)
                elif isinstance(variants_raw, list):
                    # Si ya viene como lista (parser JSONParser)
                    variants_data = variants_raw
                else:
                    raise ValueError(f"Formato de variantes inválido: {type(variants_raw)}")
                
                print(f"✅ Variantes parseadas: {variants_data}")
                print(f"✅ Cantidad de variantes: {len(variants_data)}")
                
                if not isinstance(variants_data, list) or len(variants_data) == 0:
                    errors['variants'] = ['Debe incluir al menos una variante']
                else:
                    # Validar estructura de cada variante
                    for idx, v in enumerate(variants_data):
                        print(f"\n🔹 Validando variante {idx + 1}: {v}")
                        if not isinstance(v, dict):
                            errors['variants'] = [f'Variante {idx + 1} tiene formato inválido']
                            break
                        # Opcional: validar campos específicos
                        if 'size' not in v and 'color' not in v:
                            errors['variants'] = [f'Variante {idx + 1} debe tener al menos size o color']
                            break
                        
            except json.JSONDecodeError as e:
                print(f"❌ Error parseando JSON: {str(e)}")
                errors['variants'] = [f'JSON de variantes inválido: {str(e)}']
                variants_data = None
            except Exception as e:
                print(f"❌ Error procesando variantes: {str(e)}")
                errors['variants'] = [f'Error procesando variantes: {str(e)}']
                variants_data = None
        
        # Si hay errores, retornar antes de crear nada
        if errors:
            print(f"\n❌ ERRORES DE VALIDACIÓN:")
            for field, errs in errors.items():
                print(f"   - {field}: {errs}")
            return Response(
                {'errors': errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ========== CREAR PRODUCTO ==========
        try:
            product = Product.objects.create(
                name=str(name).strip(),
                description=str(request.data.get('description', '')).strip(),
                price=price,
                categoria=categoria,
                active=request.data.get('active', 'true').lower() in ['true', '1', 'yes', 'on', True]
            )
            print(f"\n✅ PRODUCTO CREADO:")
            print(f"   - ID: {product.id}")
            print(f"   - Nombre: {product.name}")
            print(f"   - Precio: ${product.price}")
            print(f"   - Categoría: {product.categoria.nombre}")
            print(f"   - Activo: {product.active}")
            
        except Exception as e:
            print(f"❌ Error creando producto: {str(e)}")
            return Response(
                {'error': f'Error al crear producto: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ========== CREAR VARIANTES ==========
        variants_created = []
        try:
            print(f"\n📦 CREANDO {len(variants_data)} VARIANTE(S)...")
            
            for idx, variant_data in enumerate(variants_data):
                print(f"\n🔹 Procesando variante {idx + 1}:")
                print(f"   Data recibida: {variant_data}")
                
                # Extraer datos con valores por defecto seguros
                size = variant_data.get('size', None)
                color = variant_data.get('color', None)
                model_name = variant_data.get('model_name', None)
                
                # Stock: forzar a entero, mínimo 2
                stock_raw = variant_data.get('stock', 2)
                try:
                    stock = int(stock_raw)
                    if stock < 0:
                        stock = 0
                        print(f"   ⚠️ Stock negativo ajustado a 0")
                except (ValueError, TypeError):
                    stock = 2
                    print(f"   ⚠️ Stock inválido '{stock_raw}', usando default: 2")
                
                # Precio de variante (opcional, hereda del producto si no viene)
                variant_price = variant_data.get('price')
                if variant_price:
                    try:
                        variant_price = float(variant_price)
                        print(f"   ℹ️ Precio específico: ${variant_price}")
                    except (ValueError, TypeError):
                        variant_price = None
                        print(f"   ⚠️ Precio inválido, heredará del producto")
                
                # No manejamos SKU desde el backend aquí
                sku = None
                
                # CREAR VARIANTE
                variant = ProductVariant.objects.create(
                    product=product,
                    sku=sku,
                    size=size,
                    color=color,
                    model_name=model_name,
                    price=variant_price,
                    stock=stock
                )
                
                variants_created.append(variant)
                print(f"   ✅ VARIANTE CREADA:")
                print(f"      - ID: {variant.id}")
                print(f"      - Talla: {variant.size or 'N/A'}")
                print(f"      - Color: {variant.color or 'N/A'}")
                print(f"      - Stock: {variant.stock}")
                print(f"      - Precio: ${variant.price or product.price}")
                print(f"      - Disponible: {'Sí' if variant.stock > 0 else 'No'}")
            
            print(f"\n✅ TOTAL VARIANTES CREADAS: {len(variants_created)}")
            
        except Exception as e:
            print(f"\n❌ ERROR CRÍTICO CREANDO VARIANTES:")
            print(f"   {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Rollback: eliminar producto
            product.delete()
            return Response(
                {'error': f'Error al crear variantes: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # ========== SUBIR IMÁGENES ==========
        images_created = []
        files = request.FILES.getlist('images')
        
        if files:
            print(f"\n🖼️ PROCESANDO {len(files)} IMAGEN(ES)...")
            
            for idx, file in enumerate(files):
                try:
                    # Validar tamaño (5MB máx)
                    if file.size > 5 * 1024 * 1024:
                        print(f"   ⚠️ Imagen {idx+1} demasiado grande ({file.size / 1024 / 1024:.2f}MB), omitida")
                        continue
                    
                    image = ProductImage.objects.create(
                        product=product,
                        image=file,
                        is_main=(idx == 0),
                        order=idx
                    )
                    images_created.append(image)
                    print(f"   ✅ Imagen {idx+1} subida: {image.image.url if image.image else 'No URL'}")
                    
                except Exception as e:
                    print(f"   ❌ Error subiendo imagen {idx+1}: {str(e)}")
            
            print(f"✅ TOTAL IMÁGENES SUBIDAS: {len(images_created)}")
        else:
            print("\n⚠️ No se recibieron imágenes")
        
        # ========== RESPUESTA FINAL ==========
        product.refresh_from_db()
        response_data = ProductDetailSerializer(product).data
        
        print("\n" + "="*100)
        print("✅ PRODUCTO CREADO EXITOSAMENTE")
        print("="*100)
        print(f"📦 Producto ID: {response_data['id']}")
        print(f"📦 Nombre: {response_data['name']}")
        print(f"📦 Variantes: {len(response_data.get('variants', []))}")
        print(f"📦 Imágenes: {len(response_data.get('images', []))}")
        print(f"📦 Stock total: {response_data.get('total_stock', 0)}")
        print(f"📦 Disponible: {'Sí' if response_data.get('is_available', False) else 'No'}")
        print("="*100 + "\n")
        
        return Response(response_data, status=status.HTTP_201_CREATED)

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
