from rest_framework import serializers
from .models import Product, ProductImage, ProductVariant
from categorias.serializers import CategoriaSerializer


class ProductImageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProductImage
        fields = ['id', 'image_url']


class ProductVariantSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'sku', 'size', 'color', 'model_name', 'price', 'stock']

    def validate_stock(self, value):
        """Ensure stock is at least the minimum threshold (2)."""
        try:
            v = int(value)
        except Exception:
            raise serializers.ValidationError("Stock must be an integer")
        if v < 2:
            raise serializers.ValidationError("El stock mínimo permitido es 2")
        return v


class InventoryVariantSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    categoria = CategoriaSerializer(source='product.categoria', read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'product_id', 'product_name', 'categoria', 'sku', 'size', 'color', 'model_name', 'price', 'stock']


class ProductListSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    variants = ProductVariantSerializer(many=True, required=False)
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'base_price', 'images', 'variants', 'categoria', 'categoria_id', 'active']


class ProductDetailSerializer(ProductListSerializer):
    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + ['created_at', 'updated_at']

    def create(self, validated_data):
        # manejar categoria por id
        variants_data = validated_data.pop('variants', []) if 'variants' in validated_data else []
        images_data = validated_data.pop('images', []) if 'images' in validated_data else []
        categoria_id = validated_data.pop('categoria_id', None)
        if categoria_id:
            validated_data['categoria_id'] = categoria_id

        # crear producto
        product = super().create(validated_data)

        # crear variantes (asegurar stock mínimo)
        from .models import ProductVariant, ProductImage
        for v in variants_data:
            s = v.get('stock', None)
            if s is None:
                v['stock'] = 2
            else:
                try:
                    if int(s) < 2:
                        v['stock'] = 2
                except Exception:
                    v['stock'] = 2
            ProductVariant.objects.create(product=product, **v)

        # crear imágenes
        for img in images_data:
            ProductImage.objects.create(product=product, **img)

        return product

    def update(self, instance, validated_data):
        variants_data = validated_data.pop('variants', None)
        images_data = validated_data.pop('images', None)
        categoria_id = validated_data.pop('categoria_id', None)
        if categoria_id:
            instance.categoria_id = categoria_id

        # actualizar campos simples
        product = super().update(instance, validated_data)

        # si se proveen variantes, reemplazamos (simple approach)
        from .models import ProductVariant, ProductImage
        if variants_data is not None:
            # borrar existentes y crear nuevas (asegurar stock mínimo)
            ProductVariant.objects.filter(product=product).delete()
            for v in variants_data:
                s = v.get('stock', None)
                if s is None:
                    v['stock'] = 2
                else:
                    try:
                        if int(s) < 2:
                            v['stock'] = 2
                    except Exception:
                        v['stock'] = 2
                ProductVariant.objects.create(product=product, **v)

        if images_data is not None:
            ProductImage.objects.filter(product=product).delete()
            for img in images_data:
                ProductImage.objects.create(product=product, **img)

        return product