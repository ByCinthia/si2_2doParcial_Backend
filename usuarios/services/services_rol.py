from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError
from ..models import Rol
from ..serializers import RolSerializer


class RolService:
    """Servicio para la lógica de negocio de Roles"""
    
    @staticmethod
    def listar_roles():
        """
        Lista todos los roles
        Returns:
            tuple: (success, data/error, status_code)
        """
        try:
            roles = Rol.objects.all()
            serializer = RolSerializer(roles, many=True)
            return True, serializer.data, 200
        except Exception as e:
            return False, {"error": f"Error al listar roles: {str(e)}"}, 500
    
    @staticmethod
    def obtener_rol(id_rol):
        """
        Obtiene un rol por su ID
        Args:
            id_rol: ID del rol
        Returns:
            tuple: (success, data/error, status_code)
        """
        try:
            rol = Rol.objects.get(idRol=id_rol)
            serializer = RolSerializer(rol)
            return True, serializer.data, 200
        except ObjectDoesNotExist:
            return False, {"error": "Rol no encontrado"}, 404
        except Exception as e:
            return False, {"error": f"Error al obtener rol: {str(e)}"}, 500
    
    @staticmethod
    def crear_rol(data):
        """
        Crea un nuevo rol
        Args:
            data: Datos del rol a crear
        Returns:
            tuple: (success, data/error, status_code)
        """
        try:
            serializer = RolSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return True, serializer.data, 201
            return False, serializer.errors, 400
        except IntegrityError:
            return False, {"error": "Ya existe un rol con ese nombre"}, 400
        except Exception as e:
            return False, {"error": f"Error al crear rol: {str(e)}"}, 500
    
    @staticmethod
    def actualizar_rol(id_rol, data):
        """
        Actualiza un rol existente
        Args:
            id_rol: ID del rol
            data: Datos a actualizar
        Returns:
            tuple: (success, data/error, status_code)
        """
        try:
            rol = Rol.objects.get(idRol=id_rol)
            serializer = RolSerializer(rol, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return True, serializer.data, 200
            return False, serializer.errors, 400
        except ObjectDoesNotExist:
            return False, {"error": "Rol no encontrado"}, 404
        except IntegrityError:
            return False, {"error": "Ya existe un rol con ese nombre"}, 400
        except Exception as e:
            return False, {"error": f"Error al actualizar rol: {str(e)}"}, 500
    
    @staticmethod
    def eliminar_rol(id_rol):
        """
        Elimina un rol
        Args:
            id_rol: ID del rol
        Returns:
            tuple: (success, data/error, status_code)
        """
        try:
            rol = Rol.objects.get(idRol=id_rol)
            
            # Verificar si hay usuarios con este rol
            if rol.usuarios.exists():
                return False, {
                    "error": "No se puede eliminar el rol porque tiene usuarios asociados"
                }, 400
            
            rol.delete()
            return True, {"mensaje": "Rol eliminado exitosamente"}, 200
        except ObjectDoesNotExist:
            return False, {"error": "Rol no encontrado"}, 404
        except Exception as e:
            return False, {"error": f"Error al eliminar rol: {str(e)}"}, 500
    
    @staticmethod
    def buscar_rol_por_nombre(nombre):
        """
        Busca un rol por nombre
        Args:
            nombre: Nombre del rol
        Returns:
            tuple: (success, data/error, status_code)
        """
        try:
            rol = Rol.objects.get(nombre=nombre)
            serializer = RolSerializer(rol)
            return True, serializer.data, 200
        except ObjectDoesNotExist:
            return False, {"error": "Rol no encontrado"}, 404
        except Exception as e:
            return False, {"error": f"Error al buscar rol: {str(e)}"}, 500
