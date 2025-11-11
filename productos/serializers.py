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