from rest_framework import serializers
from .models import Product, ProductImage, ProductVariant

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url']

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id','sku','size','color','model_name','price','stock']

class ProductListSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id','name','description','price','base_price','images','variants','active']

    def get_price(self, obj):
        # precio mostrado por defecto: base_price. Frontend puede mostrar variantes si existen
        return obj.base_price

class ProductDetailSerializer(ProductListSerializer):
    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + ['created_at','updated_at']