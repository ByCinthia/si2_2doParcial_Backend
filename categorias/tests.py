from django.test import TestCase
from .models import Categoria


class CategoriaModelTest(TestCase):
    def test_crear_categoria(self):
        c = Categoria.objects.create(nombre='Ropa', descripcion='Categoria ropa')
        self.assertEqual(c.nombre, 'Ropa')
        self.assertTrue(c.activo)
