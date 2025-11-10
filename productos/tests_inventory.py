from django.test import TestCase
from usuarios.models import Usuario
from categorias.models import Categoria
from .models import Product, ProductVariant, InventoryMovement


class InventoryIntegrationTest(TestCase):
    def setUp(self):
        # crear rol y usuario mínimo necesario (sin permisos detallados en este test)
        from usuarios.services.services_rol import RolService
        rol, created = Categoria.objects.get_or_create(nombre='PruebaCategoria') if False else (None, None)

        # crear categoria
        self.categoria = Categoria.objects.create(nombre='TestCat')

        # crear producto y variante
        self.product = Product.objects.create(name='P1', description='d', base_price='10.00', categoria=self.categoria)
        self.variant = ProductVariant.objects.create(product=self.product, sku='SKU1', stock=10)

    def test_ajustar_stock_crea_movimiento(self):
        # ajustar stock vía servicio
        from .services.services_producto import ProductoService
        success, data, status = ProductoService.ajustar_stock(self.variant.id, delta=5, usuario=None, motivo='entrada')
        self.assertTrue(success)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 15)
        mov = InventoryMovement.objects.filter(variant=self.variant).first()
        self.assertIsNotNone(mov)
        self.assertEqual(mov.delta, 5)
