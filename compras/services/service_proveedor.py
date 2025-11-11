from compras.models import Proveedor
from compras.serializers import ProveedorSerializer
from rest_framework import status


class ProveedorService:
    """Servicio para manejar la lógica de negocio de Proveedores"""
    
    @staticmethod
    def listar_proveedores():
        """Lista todos los proveedores"""
        try:
            proveedores = Proveedor.objects.all()
            serializer = ProveedorSerializer(proveedores, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def obtener_proveedor(id_proveedor):
        """Obtiene un proveedor por ID"""
        try:
            proveedor = Proveedor.objects.get(idProveedor=id_proveedor)
            serializer = ProveedorSerializer(proveedor)
            return True, serializer.data, status.HTTP_200_OK
        except Proveedor.DoesNotExist:
            return False, {"error": "Proveedor no encontrado"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def crear_proveedor(data):
        """Crea un nuevo proveedor"""
        try:
            serializer = ProveedorSerializer(data=data)
            if not serializer.is_valid():
                return False, serializer.errors, status.HTTP_400_BAD_REQUEST
            
            proveedor = serializer.save()
            return True, ProveedorSerializer(proveedor).data, status.HTTP_201_CREATED
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def actualizar_proveedor(id_proveedor, data):
        """Actualiza un proveedor existente"""
        try:
            proveedor = Proveedor.objects.get(idProveedor=id_proveedor)
            serializer = ProveedorSerializer(proveedor, data=data, partial=True)
            
            if not serializer.is_valid():
                return False, serializer.errors, status.HTTP_400_BAD_REQUEST
            
            proveedor_actualizado = serializer.save()
            return True, ProveedorSerializer(proveedor_actualizado).data, status.HTTP_200_OK
        except Proveedor.DoesNotExist:
            return False, {"error": "Proveedor no encontrado"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def eliminar_proveedor(id_proveedor):
        """Elimina un proveedor"""
        try:
            proveedor = Proveedor.objects.get(idProveedor=id_proveedor)
            
            # Verificar si tiene compras asociadas
            if proveedor.compras.exists():
                return False, {
                    "error": "No se puede eliminar el proveedor porque tiene compras asociadas"
                }, status.HTTP_400_BAD_REQUEST
            
            proveedor.delete()
            return True, {"mensaje": "Proveedor eliminado correctamente"}, status.HTTP_200_OK
        except Proveedor.DoesNotExist:
            return False, {"error": "Proveedor no encontrado"}, status.HTTP_404_NOT_FOUND
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
    
    @staticmethod
    def buscar_proveedores(query):
        """Busca proveedores por nombre o email"""
        try:
            proveedores = Proveedor.objects.filter(
                nombre__icontains=query
            ) | Proveedor.objects.filter(
                email__icontains=query
            )
            
            serializer = ProveedorSerializer(proveedores, many=True)
            return True, serializer.data, status.HTTP_200_OK
        except Exception as e:
            return False, {"error": str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR
