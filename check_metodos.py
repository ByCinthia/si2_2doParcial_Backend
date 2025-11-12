import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'si2Backend.settings')
django.setup()

from ventas.models import MetodoPago

metodos = list(MetodoPago.objects.values('idMetodoPago', 'nombre', 'descripcion'))
print(json.dumps(metodos, indent=2, default=str))
