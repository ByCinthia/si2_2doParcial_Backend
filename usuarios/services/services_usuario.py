from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404

from usuarios.models import Usuario, Rol
from usuarios.serializers import (
    UsuarioDetailSerializer,
    UsuarioCreateSerializer,
    UsuarioSerializer,  # ← FALTABA
    UsuarioLoginSerializer,  # ← FALTABA
)


class UsuarioService:
    """Servicio para la lógica de negocio de Usuarios"""

    @staticmethod
    def _puede_crear_rol(usuario_empleado, rol_objetivo):
        """Define si el empleado puede asignar/crear un usuario con rol_objetivo"""
        if not usuario_empleado or not hasattr(usuario_empleado, 'rol') or not usuario_empleado.rol:
            return False
        nombre = usuario_empleado.rol.nombre
        objetivo = rol_objetivo.nombre
        if nombre == 'SuperAdmin':
            return True
        if nombre in ['Trabajador', 'Vendedor']:
            return objetivo in ['Cliente', 'Cajero', 'Trabajador', 'Vendedor']
        if nombre == 'Cajero':
            return objetivo == 'Cliente'
        return False

    @staticmethod
    def listar_usuarios():
        """
        Lista todos los usuarios
        Returns:
            tuple: (success, data/error, status_code)
        """
        try:
            usuarios = Usuario.objects.select_related('rol').all()
            serializer = UsuarioDetailSerializer(usuarios, many=True)
            return True, serializer.data, 200
        except Exception as e:
            return False, {"error": f"Error al listar usuarios: {str(e)}"}, 500
    
    @staticmethod
    def obtener_usuario(id_usuario):
        """
        Obtiene un usuario por su ID
        Args:
            id_usuario: ID del usuario
        Returns:
            tuple: (success, data/error, status_code)
        """
        try:
            usuario = Usuario.objects.select_related('rol').get(idUsuario=id_usuario)
            serializer = UsuarioDetailSerializer(usuario)
            return True, serializer.data, 200
        except ObjectDoesNotExist:
            return False, {"error": "Usuario no encontrado"}, 404
        except Exception as e:
            return False, {"error": f"Error al obtener usuario: {str(e)}"}, 500
    
    @staticmethod
    def crear_usuario(data, creado_por=None):
        """
        Crea un usuario (cliente o trabajador).
        - creado_por: instancia Usuario que realiza la creación (para auditoría y permisos).
        """
        try:
            # role must be provided (idRol o nombre)
            rol_id = data.get('rol') or data.get('rol_id') or data.get('idRol')
            if not rol_id:
                return False, {"error": "Debe especificar el rol (campo 'rol' o 'idRol')"}, 400

            # obtener rol
            try:
                # aceptar id numeric o nombre
                if isinstance(rol_id, int) or (isinstance(rol_id, str) and rol_id.isdigit()):
                    rol_obj = Rol.objects.get(idRol=int(rol_id))
                else:
                    rol_obj = Rol.objects.get(nombre=rol_id)
            except Rol.DoesNotExist:
                return False, {"error": "Rol especificado no existe"}, 400

            # verificar permisos del creador (solo si se proporciona creado_por)
            if creado_por:
                if not UsuarioService._puede_crear_rol(creado_por, rol_obj):
                    return False, {"error": "No tienes permisos para crear usuarios con ese rol"}, 403

            # preparar datos para el serializer (forzar rol correcto)
            payload = data.copy()
            payload['idRol'] = rol_obj.idRol  # Usar idRol en lugar de rol
            payload['activo'] = payload.get('activo', True)

            serializer = UsuarioCreateSerializer(data=payload)
            if not serializer.is_valid():
                return False, {"errors": serializer.errors}, 400

            usuario = serializer.save()
            return True, {
                "message": "Usuario creado exitosamente",
                "usuario": UsuarioDetailSerializer(usuario).data
            }, 201

        except IntegrityError as e:
            if 'username' in str(e):
                return False, {"error": "El nombre de usuario ya está registrado"}, 400
            elif 'email' in str(e):
                return False, {"error": "El email ya está registrado"}, 400
            return False, {"error": "Error de integridad: " + str(e)}, 400
        except Exception as e:
            return False, {"error": "Error interno: " + str(e)}, 500
    
    @staticmethod
    def actualizar_usuario(id_usuario, data):
        """
        Actualiza un usuario existente
        Args:
            id_usuario: ID del usuario
            data: Datos a actualizar
        Returns:
            tuple: (success, data/error, status_code)
        """
        try:
            usuario = Usuario.objects.get(idUsuario=id_usuario)
            
            # Validar rol si se está actualizando
            if 'idRol' in data:
                if not Rol.objects.filter(idRol=data['idRol']).exists():
                    return False, {"error": "El rol especificado no existe"}, 400
                # Mapear idRol a rol para el modelo
                data['rol_id'] = data.pop('idRol')
            
            # Validar username único
            if 'username' in data and data['username'] != usuario.username:
                if Usuario.objects.filter(username=data['username']).exists():
                    return False, {"error": "El nombre de usuario ya está registrado"}, 400
            
            # Validar email único
            if 'email' in data and data['email'] != usuario.email:
                if Usuario.objects.filter(email=data['email']).exists():
                    return False, {"error": "El email ya está registrado"}, 400
            
            serializer = UsuarioSerializer(usuario, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                response_serializer = UsuarioDetailSerializer(usuario)
                return True, response_serializer.data, 200
            return False, serializer.errors, 400
        except ObjectDoesNotExist:
            return False, {"error": "Usuario no encontrado"}, 404
        except Exception as e:
            return False, {"error": f"Error al actualizar usuario: {str(e)}"}, 500
    
    @staticmethod
    def eliminar_usuario(id_usuario):
        """
        Elimina un usuario (soft delete)
        Args:
            id_usuario: ID del usuario
        Returns:
            tuple: (success, data/error, status_code)
        """
        try:
            usuario = Usuario.objects.get(idUsuario=id_usuario)
            usuario.activo = False
            usuario.save()
            return True, {"mensaje": "Usuario desactivado exitosamente"}, 200
        except ObjectDoesNotExist:
            return False, {"error": "Usuario no encontrado"}, 404
        except Exception as e:
            return False, {"error": f"Error al eliminar usuario: {str(e)}"}, 500
    
    @staticmethod
    def eliminar_usuario_permanente(id_usuario):
        """
        Elimina un usuario permanentemente
        Args:
            id_usuario: ID del usuario
        Returns:
            tuple: (success, data/error, status_code)
        """
        try:
            usuario = Usuario.objects.get(idUsuario=id_usuario)
            usuario.delete()
            return True, {"mensaje": "Usuario eliminado permanentemente"}, 200
        except ObjectDoesNotExist:
            return False, {"error": "Usuario no encontrado"}, 404
        except Exception as e:
            return False, {"error": f"Error al eliminar usuario: {str(e)}"}, 500
    
    @staticmethod
    def login(data):
        """
        Autentica un usuario y genera tokens JWT
        Args:
            data: Credenciales de login (username/email, password)
        Returns:
            tuple: (success, data/error, status_code)
        """
        try:
            serializer = UsuarioLoginSerializer(data=data)
            if not serializer.is_valid():
                return False, serializer.errors, 400

            validated = serializer.validated_data
            email = validated.get('email')
            username = validated.get('username')
            password = validated.get('password')

            # Buscar usuario por email o username
            if email:
                usuario = Usuario.objects.select_related('rol').filter(email=email).first()
            elif username:
                usuario = Usuario.objects.select_related('rol').filter(username=username).first()
            else:
                usuario = None
            
            if not usuario:
                return False, {"error": "Credenciales inválidas"}, 401

            # Verificar si está activo
            if not usuario.activo:
                return False, {"error": "Usuario inactivo"}, 403

            # Verificar contraseña
            if not usuario.check_password(password):
                return False, {"error": "Credenciales inválidas"}, 401

            # Generar tokens JWT
            refresh = RefreshToken.for_user(usuario)

            return True, {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "usuario": UsuarioDetailSerializer(usuario).data
            }, 200
        except Exception as e:
            return False, {"error": f"Error en el login: {str(e)}"}, 500
    
    @staticmethod
    def cambiar_password(id_usuario, password_actual, password_nueva):
        """
        Cambia la contraseña de un usuario
        Args:
            id_usuario: ID del usuario
            password_actual: Contraseña actual
            password_nueva: Nueva contraseña
        Returns:
            tuple: (success, data/error, status_code)
        """
        try:
            usuario = Usuario.objects.get(idUsuario=id_usuario)
            
            # Verificar contraseña actual
            if not usuario.check_password(password_actual):
                return False, {"error": "La contraseña actual es incorrecta"}, 400
            
            # Validar longitud de nueva contraseña
            if len(password_nueva) < 6:
                return False, {"error": "La contraseña debe tener al menos 6 caracteres"}, 400
            
            # Cambiar contraseña
            usuario.set_password(password_nueva)
            usuario.save()
            
            return True, {"mensaje": "Contraseña actualizada exitosamente"}, 200
        except ObjectDoesNotExist:
            return False, {"error": "Usuario no encontrado"}, 404
        except Exception as e:
            return False, {"error": f"Error al cambiar contraseña: {str(e)}"}, 500
    
    @staticmethod
    def buscar_usuarios(query):
        """
        Busca usuarios por username o email
        Args:
            query: Término de búsqueda
        Returns:
            tuple: (success, data/error, status_code)
        """
        try:
            usuarios = Usuario.objects.select_related('rol').filter(
                Q(username__icontains=query) | Q(email__icontains=query)
            )
            serializer = UsuarioSerializer(usuarios, many=True)
            return True, serializer.data, 200
        except Exception as e:
            return False, {"error": f"Error al buscar usuarios: {str(e)}"}, 500
    
    @staticmethod
    def actualizar_fcm_token(id_usuario, fcm_token):
        """
        Actualiza el FCM token de un usuario
        Args:
            id_usuario: ID del usuario
            fcm_token: Nuevo FCM token
        Returns:
            tuple: (success, data/error, status_code)
        """
        try:
            usuario = Usuario.objects.get(idUsuario=id_usuario)
            usuario.fcmToken = fcm_token
            usuario.save()
            return True, {"mensaje": "FCM token actualizado exitosamente"}, 200
        except ObjectDoesNotExist:
            return False, {"error": "Usuario no encontrado"}, 404
        except Exception as e:
            return False, {"error": f"Error al actualizar FCM token: {str(e)}"}, 500
    
    @staticmethod
    def registrar_cliente(data):
        """
        Registra un nuevo usuario con rol de Cliente
        Args:
            data: Datos del cliente a registrar (username, email, password, fcmToken opcional)
        Returns:
            tuple: (success, data/error, status_code)
        """
        try:
            # Buscar el rol "Cliente"
            try:
                rol_cliente = Rol.objects.get(nombre='Cliente')
            except ObjectDoesNotExist:
                return False, {
                    "error": "No se encontró el rol 'Cliente' en el sistema. Contacte al administrador."
                }, 500
            
            # Validar que el username no exista
            if Usuario.objects.filter(username=data.get('username')).exists():
                return False, {"error": "El nombre de usuario ya está registrado"}, 400
            
            # Validar que el email no exista
            if Usuario.objects.filter(email=data.get('email')).exists():
                return False, {"error": "El email ya está registrado"}, 400
            
            # Validar campos requeridos
            if not data.get('username'):
                return False, {"error": "El nombre de usuario es requerido"}, 400
            if not data.get('email'):
                return False, {"error": "El email es requerido"}, 400
            if not data.get('password'):
                return False, {"error": "La contraseña es requerida"}, 400
            
            # Validar longitud de contraseña
            if len(data.get('password', '')) < 6:
                return False, {"error": "La contraseña debe tener al menos 6 caracteres"}, 400
            
            # Crear el usuario con rol Cliente
            usuario_data = {
                'username': data.get('username'),
                'email': data.get('email'),
                'password': data.get('password'),
                'idRol': rol_cliente.idRol,
                'fcmToken': data.get('fcmToken', None)
            }
            
            serializer = UsuarioCreateSerializer(data=usuario_data)
            if serializer.is_valid():
                # El serializer ya maneja la creación correctamente
                usuario = serializer.save()
                
                # Generar tokens JWT para login automático
                refresh = RefreshToken.for_user(usuario)
                
                response_serializer = UsuarioDetailSerializer(usuario)
                return True, {
                    "mensaje": "Cliente registrado exitosamente",
                    "usuario": response_serializer.data,
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token)
                    }
                }, 201
            return False, serializer.errors, 400
        except IntegrityError as e:
            if 'username' in str(e):
                return False, {"error": "El nombre de usuario ya está registrado"}, 400
            elif 'email' in str(e):
                return False, {"error": "El email ya está registrado"}, 400
            return False, {"error": "Error de integridad en los datos"}, 400
        except Exception as e:
            return False, {"error": f"Error al registrar cliente: {str(e)}"}, 500
