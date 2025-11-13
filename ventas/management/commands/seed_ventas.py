import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from ventas.models import Venta, DetalleVenta
from productos.models import Product
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Genera datos de prueba de ventas para un mes'

    def add_arguments(self, parser):
        parser.add_argument('--dias', type=int, default=30, help='Número de días de datos a generar')
        parser.add_argument('--ventas-por-dia', type=int, default=5, help='Ventas promedio por día')

    def handle(self, *args, **options):
        dias = options['dias']
        ventas_por_dia = options['ventas_por_dia']
        
        # Verificar que hay usuarios y productos
        usuarios = list(User.objects.all())
        productos = list(Product.objects.filter(active=True))
        
        if not usuarios:
            self.stdout.write(self.style.ERROR('No hay usuarios en la BD. Crea al menos uno.'))
            return
            
        if not productos:
            self.stdout.write(self.style.ERROR('No hay productos activos. Crea algunos primero.'))
            return

        self.stdout.write(f'Generando {dias} días de ventas con ~{ventas_por_dia} ventas/día...')
        
        fecha_fin = timezone.now()
        fecha_inicio = fecha_fin - timedelta(days=dias)
        
        total_ventas_creadas = 0
        
        for i in range(dias):
            fecha_venta = fecha_inicio + timedelta(days=i)
            # Variar cantidad de ventas por día (80% a 120% del promedio)
            num_ventas = random.randint(int(ventas_por_dia * 0.8), int(ventas_por_dia * 1.2))
            
            for _ in range(num_ventas):
                # Usuario aleatorio
                usuario = random.choice(usuarios)
                
                # Crear venta
                venta = Venta.objects.create(
                    usuario=usuario,
                    fecha=fecha_venta + timedelta(
                        hours=random.randint(8, 20),
                        minutes=random.randint(0, 59)
                    ),
                    total=Decimal('0')
                )
                
                # Añadir entre 1 y 4 productos por venta
                num_items = random.randint(1, 4)
                total_venta = Decimal('0')
                
                productos_venta = random.sample(productos, min(num_items, len(productos)))
                
                for producto in productos_venta:
                    cantidad = random.randint(1, 3)
                    # Usar precio del producto con pequeña variación (descuentos, etc)
                    precio_base = Decimal(str(producto.price))
                    variacion = Decimal(str(random.uniform(0.9, 1.0)))  # 0% a 10% descuento
                    precio_unitario = (precio_base * variacion).quantize(Decimal('0.01'))
                    subtotal = precio_unitario * cantidad
                    
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                        subtotal=subtotal
                    )
                    
                    total_venta += subtotal
                
                # Actualizar total de venta
                venta.total = total_venta
                venta.save()
                
                total_ventas_creadas += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Se crearon {total_ventas_creadas} ventas con datos aleatorios'
            )
        )
        
        # Mostrar estadísticas
        from django.db.models import Sum
        total_ingresos = Venta.objects.aggregate(total=Sum('total'))['total'] or 0
        self.stdout.write(f'Total de ingresos generados: ${total_ingresos}')