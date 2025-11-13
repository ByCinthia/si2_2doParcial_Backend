from rest_framework import serializers
from .models import Product, ProductImage, ProductVariant
from categorias.serializers import CategoriaSerializer


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'alt_text', 'is_main', 'order']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer para variantes - SOLO muestra precios y stock"""
    sale_price = serializers.SerializerMethodField()
    cost_price = serializers.SerializerMethodField()
    is_available = serializers.BooleanField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'size', 'color', 'model_name', 
            'price', 'cost',  # Valores originales (internos)
            'sale_price', 'cost_price',  # Valores efectivos
            'stock', 'is_available', 'is_low_stock'
        ]
    
    def get_sale_price(self, obj):
        """Precio de venta efectivo"""
        return str(obj.get_sale_price())
    
    def get_cost_price(self, obj):
        """Precio de costo efectivo"""
        return str(obj.get_cost_price())


class ProductListSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    categoria = CategoriaSerializer(read_only=True)
    total_stock = serializers.IntegerField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 
            'cost_price', 'price',  # Precios base
            'images', 'variants', 
            'categoria', 'active', 
            'total_stock', 'is_available',
            'created_at'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    categoria = CategoriaSerializer(read_only=True)
    total_stock = serializers.IntegerField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    available_variants = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 
            'cost_price', 'price',
            'categoria', 'images', 
            'variants', 'available_variants', 
            'active', 'total_stock', 
            'is_available', 'created_at', 'updated_at'
        ]
    
    def get_available_variants(self, obj):
        available = obj.variants.filter(stock__gt=0)
        return ProductVariantSerializer(available, many=True).data


class InventoryVariantSerializer(serializers.ModelSerializer):
    """Serializer para inventario - SOLO stock y precios, sin ganancias"""
    id = serializers.IntegerField(read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    categoria = CategoriaSerializer(source='product.categoria', read_only=True)
    sale_price = serializers.SerializerMethodField()
    cost_price = serializers.SerializerMethodField()
    is_available = serializers.BooleanField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product_id', 'product_name', 'categoria',
            'size', 'color', 'model_name',
            'sale_price', 'cost_price',  # Solo precios
            'stock', 'is_available', 'is_low_stock'
        ]
    
    def get_sale_price(self, obj):
        return str(obj.get_sale_price())
    
    def get_cost_price(self, obj):
        return str(obj.get_cost_price())


class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True, required=False)
    images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'cost_price', 'price',
            'categoria', 'active', 'created_at', 'updated_at',
            'variants', 'images', 'total_stock', 'is_available'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_stock', 'is_available']
    
    def create(self, validated_data):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # 🔍 Log para debug
            logger.info(f"validated_data recibido: {validated_data}")
            
            # Extraer variantes
            variants_data = validated_data.pop('variants', [])
            
            # Si no vinieron en validated_data, intentar desde context
            if not variants_data:
                request = self.context.get('request')
                if request:
                    variants_raw = request.data.get('variants')
                    if isinstance(variants_raw, str):
                        import json
                        variants_data = json.loads(variants_raw)
                    elif isinstance(variants_raw, list):
                        variants_data = variants_raw
            
            logger.info(f"variants_data procesado: {variants_data}")
            
            if not variants_data:
                raise serializers.ValidationError({
                    'variants': 'Debe incluir al menos una variante'
                })
            
            # Crear producto
            product = Product.objects.create(**validated_data)
            logger.info(f"Producto creado: {product.id}")
            
            # Crear variantes
            for idx, variant_data in enumerate(variants_data):
                logger.info(f"Creando variante {idx}: {variant_data}")
                
                # Limpiar valores None
                variant_clean = {k: v for k, v in variant_data.items() if v is not None}
                
                ProductVariant.objects.create(
                    product=product,
                    **variant_clean
                )
            
            logger.info(f"Producto {product.id} creado con {len(variants_data)} variantes")
            return product
            
        except Exception as e:
            logger.error(f"Error al crear producto: {str(e)}", exc_info=True)
            raise