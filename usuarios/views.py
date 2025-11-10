from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UsuarioLoginSerializer, UsuarioDetailSerializer
from .permissions import IsSuperAdmin, CanManageUsers, CanCreateClients, CanManageRoles
from .services.services_rol import RolService
from .services.services_usuario import UsuarioService
import logging


logger = logging.getLogger(__name__)


# ==================== VISTAS DE ROL ====================

class RolListCreateView(APIView):
    """Vista para listar y crear roles - Solo SuperAdmin"""
    
    def get_permissions(self):
        """GET: cualquier usuario autenticado puede ver roles, POST: solo SuperAdmin"""
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [CanManageRoles()]
    
    def get(self, request):
        """Lista todos los roles"""
        success, data, status_code = RolService.listar_roles()
        return Response(data, status=status_code)
    
    def post(self, request):
        """Crea un nuevo rol - Solo SuperAdmin"""
        success, data, status_code = RolService.crear_rol(request.data)
        return Response(data, status=status_code)


class RolDetailView(APIView):
    """Vista para obtener, actualizar y eliminar un rol - Solo SuperAdmin"""
    permission_classes = [CanManageRoles]
    
    def get(self, request, id_rol):
        """Obtiene un rol por ID"""
        success, data, status_code = RolService.obtener_rol(id_rol)
        return Response(data, status=status_code)
    
    def put(self, request, id_rol):
        """Actualiza un rol"""
        success, data, status_code = RolService.actualizar_rol(id_rol, request.data)
        return Response(data, status=status_code)
    
    def patch(self, request, id_rol):
        """Actualiza parcialmente un rol"""
        success, data, status_code = RolService.actualizar_rol(id_rol, request.data)
        return Response(data, status=status_code)
    
    def delete(self, request, id_rol):
        """Elimina un rol"""
        success, data, status_code = RolService.eliminar_rol(id_rol)
        return Response(data, status=status_code)


class RolBuscarView(APIView):
    """Vista para buscar rol por nombre"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Busca un rol por nombre"""
        nombre = request.query_params.get('nombre', '')
        if not nombre:
            return Response({"error": "Debe proporcionar un nombre"}, status=400)
        success, data, status_code = RolService.buscar_rol_por_nombre(nombre)
        return Response(data, status=status_code)


# ==================== VISTAS DE USUARIO ====================

class UsuarioListCreateView(APIView):
    """Vista para listar y crear usuarios"""
    
    def get_permissions(self):
        """GET: usuarios autenticados, POST: quien puede gestionar usuarios"""
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [CanManageUsers()]
    
    def get(self, request):
        """Lista todos los usuarios"""
        success, data, status_code = UsuarioService.listar_usuarios()
        return Response(data, status=status_code)
    
    def post(self, request):
        """Crea un nuevo usuario - Solo SuperAdmin, Trabajador, Vendedor"""
        success, data, status_code = UsuarioService.crear_usuario(request.data)
        return Response(data, status=status_code)


class UsuarioDetailView(APIView):
    """Vista para obtener, actualizar y eliminar un usuario"""
    permission_classes = [CanManageUsers]
    
    def get(self, request, id_usuario):
        """Obtiene un usuario por ID"""
        success, data, status_code = UsuarioService.obtener_usuario(id_usuario)
        return Response(data, status=status_code)
    
    def put(self, request, id_usuario):
        """Actualiza un usuario"""
        success, data, status_code = UsuarioService.actualizar_usuario(id_usuario, request.data)
        return Response(data, status=status_code)
    
    def patch(self, request, id_usuario):
        """Actualiza parcialmente un usuario"""
        success, data, status_code = UsuarioService.actualizar_usuario(id_usuario, request.data)
        return Response(data, status=status_code)
    
    def delete(self, request, id_usuario):
        """Desactiva un usuario (soft delete)"""
        success, data, status_code = UsuarioService.eliminar_usuario(id_usuario)
        return Response(data, status=status_code)


class UsuarioDeletePermanentView(APIView):
    """Vista para eliminar permanentemente un usuario - Solo SuperAdmin"""
    permission_classes = [IsSuperAdmin]
    
    def delete(self, request, id_usuario):
        """Elimina permanentemente un usuario"""
        success, data, status_code = UsuarioService.eliminar_usuario_permanente(id_usuario)
        return Response(data, status=status_code)


class UsuarioLoginView(APIView):
    """Vista para login de usuarios"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Debug: mostrar qué datos llegan (sin mostrar password)
        debug_data = {k: v for k, v in request.data.items() if k != 'password'}
        logger.info(f"Intento de login: {debug_data}")
        
        serializer = UsuarioLoginSerializer(data=request.data)
        if not serializer.is_valid():
            errors = serializer.errors
            logger.warning(f"Error de validación en login: {errors}")
            
            # Normalizar errores a {"error": "mensaje legible"}
            msg = None
            if 'non_field_errors' in errors:
                first = errors['non_field_errors'][0]
                msg = first if isinstance(first, str) else str(first)
            else:
                # tomar el primer campo con error
                first_field = next(iter(errors))
                val = errors[first_field]
                if isinstance(val, list) and val:
                    msg = val[0]
                else:
                    msg = str(val)
            return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data.get('user')
        if not user:
            logger.error("Usuario no encontrado en validated_data")
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_401_UNAUTHORIZED)

        logger.info(f"Login exitoso para usuario: {user.username} (ID: {user.idUsuario})")
        
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "usuario": UsuarioDetailSerializer(user).data
        }, status=status.HTTP_200_OK)


class UsuarioCambiarPasswordView(APIView):
    """Vista para cambiar contraseña de usuario"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Cambia la contraseña de un usuario"""
        id_usuario = request.data.get('id_usuario')
        password_actual = request.data.get('password_actual')
        password_nueva = request.data.get('password_nueva')
        
        if not all([id_usuario, password_actual, password_nueva]):
            return Response({
                "error": "Debe proporcionar id_usuario, password_actual y password_nueva"
            }, status=400)
        
        success, data, status = UsuarioService.cambiar_password(
            id_usuario, password_actual, password_nueva
        )
        return Response(data, status=status)


class UsuarioBuscarView(APIView):
    """Vista para buscar usuarios"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Busca usuarios por username o email"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({"error": "Debe proporcionar un término de búsqueda (q)"}, status=400)
        success, data, status = UsuarioService.buscar_usuarios(query)
        return Response(data, status=status)


class UsuarioActualizarFCMTokenView(APIView):
    """Vista para actualizar FCM token"""
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, id_usuario):
        """Actualiza el FCM token de un usuario"""
        fcm_token = request.data.get('fcmToken')
        if not fcm_token:
            return Response({"error": "Debe proporcionar el fcmToken"}, status=400)
        
        success, data, status = UsuarioService.actualizar_fcm_token(id_usuario, fcm_token)
        return Response(data, status=status)


class UsuarioRegistrarView(APIView):
    """Vista para registrar nuevos usuarios (solo personal autorizado)"""
    permission_classes = [CanManageUsers]  # SuperAdmin, Trabajador, Vendedor (según tu permiso)

    def post(self, request):
        """
        Crear un nuevo usuario (cliente o trabajador) — solo personal autorizado.
        Pasa request.user al servicio para control de permisos y auditoría.
        """
        success, data, status_code = UsuarioService.crear_usuario(request.data, creado_por=request.user)
        return Response(data, status=status_code)
