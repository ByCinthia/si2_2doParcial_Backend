from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .services.services_rol import RolService
from .services.services_usuario import UsuarioService


# ==================== VISTAS DE ROL ====================

class RolListCreateView(APIView):
    """Vista para listar y crear roles"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Lista todos los roles"""
        success, data, status = RolService.listar_roles()
        return Response(data, status=status)
    
    def post(self, request):
        """Crea un nuevo rol"""
        success, data, status = RolService.crear_rol(request.data)
        return Response(data, status=status)


class RolDetailView(APIView):
    """Vista para obtener, actualizar y eliminar un rol"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_rol):
        """Obtiene un rol por ID"""
        success, data, status = RolService.obtener_rol(id_rol)
        return Response(data, status=status)
    
    def put(self, request, id_rol):
        """Actualiza un rol"""
        success, data, status = RolService.actualizar_rol(id_rol, request.data)
        return Response(data, status=status)
    
    def patch(self, request, id_rol):
        """Actualiza parcialmente un rol"""
        success, data, status = RolService.actualizar_rol(id_rol, request.data)
        return Response(data, status=status)
    
    def delete(self, request, id_rol):
        """Elimina un rol"""
        success, data, status = RolService.eliminar_rol(id_rol)
        return Response(data, status=status)


class RolBuscarView(APIView):
    """Vista para buscar rol por nombre"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Busca un rol por nombre"""
        nombre = request.query_params.get('nombre', '')
        if not nombre:
            return Response({"error": "Debe proporcionar un nombre"}, status=400)
        success, data, status = RolService.buscar_rol_por_nombre(nombre)
        return Response(data, status=status)


# ==================== VISTAS DE USUARIO ====================

class UsuarioListCreateView(APIView):
    """Vista para listar y crear usuarios"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Lista todos los usuarios"""
        success, data, status = UsuarioService.listar_usuarios()
        return Response(data, status=status)
    
    def post(self, request):
        """Crea un nuevo usuario"""
        success, data, status = UsuarioService.crear_usuario(request.data)
        return Response(data, status=status)


class UsuarioDetailView(APIView):
    """Vista para obtener, actualizar y eliminar un usuario"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id_usuario):
        """Obtiene un usuario por ID"""
        success, data, status = UsuarioService.obtener_usuario(id_usuario)
        return Response(data, status=status)
    
    def put(self, request, id_usuario):
        """Actualiza un usuario"""
        success, data, status = UsuarioService.actualizar_usuario(id_usuario, request.data)
        return Response(data, status=status)
    
    def patch(self, request, id_usuario):
        """Actualiza parcialmente un usuario"""
        success, data, status = UsuarioService.actualizar_usuario(id_usuario, request.data)
        return Response(data, status=status)
    
    def delete(self, request, id_usuario):
        """Desactiva un usuario (soft delete)"""
        success, data, status = UsuarioService.eliminar_usuario(id_usuario)
        return Response(data, status=status)


class UsuarioDeletePermanentView(APIView):
    """Vista para eliminar permanentemente un usuario"""
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, id_usuario):
        """Elimina permanentemente un usuario"""
        success, data, status = UsuarioService.eliminar_usuario_permanente(id_usuario)
        return Response(data, status=status)


class UsuarioLoginView(APIView):
    """Vista para login de usuarios"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Autentica un usuario y devuelve tokens JWT"""
        success, data, status = UsuarioService.login(request.data)
        return Response(data, status=status)


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
    """Vista para registrar nuevos clientes"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Registra un nuevo cliente en el sistema.
        El rol 'Cliente' se asigna automáticamente.
        Retorna el usuario creado y tokens JWT para login automático.
        """
        success, data, status = UsuarioService.registrar_cliente(request.data)
        return Response(data, status=status)
