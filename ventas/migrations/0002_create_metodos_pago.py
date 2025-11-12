from django.db import migrations


def create_metodos_pago(apps, schema_editor):
    MetodoPago = apps.get_model('ventas', 'MetodoPago')
    # Evitar duplicados
    MetodoPago.objects.get_or_create(nombre='Tarjeta', defaults={'descripcion': 'Pago con tarjeta de crédito/débito'})
    MetodoPago.objects.get_or_create(nombre='Efectivo', defaults={'descripcion': 'Pago en efectivo'})


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_metodos_pago),
    ]
