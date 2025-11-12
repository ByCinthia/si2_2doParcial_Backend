from ventas.models import MetodoPago
from ventas.serializers import MetodoPagoSerializer
from rest_framework import status


class MetodoPagoService:
    """Servicio para manejar métodos de pago"""
    
    @staticmethod
    def listar_metodos_pago():
        """Lista todos los métodos de pago disponibles"""
        try:
            metodos = MetodoPago.objects.all()
            serializer = MetodoPagoSerializer(metodos, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def obtener_metodo_pago(id_metodo):
        """Obtiene un método de pago por ID"""
        try:
            metodo = MetodoPago.objects.get(idMetodoPago=id_metodo)
            serializer = MetodoPagoSerializer(metodo)
            return True, serializer.data, status.HTTP_200_OK
        except MetodoPago.DoesNotExist:
            return False, {"error": "Método de pago no encontrado"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def crear_metodo_pago(data):
        """Crea un nuevo método de pago"""
        try:
            serializer = MetodoPagoSerializer(data=data)
            if not serializer.is_valid():
                return False, serializer.errors, status.HTTP_400_BAD_REQUEST
            
            metodo = serializer.save()
            return True, MetodoPagoSerializer(metodo).data, status.HTTP_201_CREATED
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
