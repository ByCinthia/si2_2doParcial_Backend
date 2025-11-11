from rest_framework import serializers
from .models import InventoryMovement, ProductImage


class InventoryMovementSerializer(serializers.ModelSerializer):
    usuario = serializers.SerializerMethodField()

    class Meta:
        model = InventoryMovement
        fields = ['id', 'variant', 'usuario', 'previous_stock', 'new_stock', 'delta', 'motivo', 'fecha']

    def get_usuario(self, obj):
        if obj.usuario:
            return {'id': obj.usuario.idUsuario, 'username': obj.usuario.username, 'email': obj.usuario.email}
        return None


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'product', 'image', 'alt_text', 'is_main', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']
