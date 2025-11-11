from django.db import transaction
from productos.models import Product
from rest_framework import serializers

class YourSerializer(serializers.Serializer):
    # Your serializer fields here

    def create(self, validated_data):
        from django.db import transaction
        from productos.models import Product

        with transaction.atomic():
            # Your create logic here
            pid = validated_data.get('product_id')
            if pid:
                try:
                    producto_obj = Product.objects.get(pk=pid)
                except Product.DoesNotExist:
                    producto_obj = None

        # Return the created object or any other relevant data
        return producto_obj