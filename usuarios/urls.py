from django.urls import path
from .views import (
    # Vistas de Rol
    RolListCreateView,
    RolDetailView,
    RolBuscarView,
    # Vistas de Usuario
    UsuarioListCreateView,
    UsuarioDetailView,
    UsuarioDeletePermanentView,
    UsuarioLoginView,
    UsuarioRegistrarView,
    UsuarioCambiarPasswordView,
    UsuarioBuscarView,
    UsuarioActualizarFCMTokenView,
)

app_name = 'usuarios'

urlpatterns = [
    # ==================== RUTAS DE ROL ====================
    # GET /api/usuarios/roles/ - Listar todos los roles
    # POST /api/usuarios/roles/ - Crear un nuevo rol
    path('roles/', RolListCreateView.as_view(), name='rol-list-create'),
    
    # GET /api/usuarios/roles/<id>/ - Obtener un rol
    # PUT /api/usuarios/roles/<id>/ - Actualizar un rol completamente
    # PATCH /api/usuarios/roles/<id>/ - Actualizar un rol parcialmente
    # DELETE /api/usuarios/roles/<id>/ - Eliminar un rol
    path('roles/<int:id_rol>/', RolDetailView.as_view(), name='rol-detail'),
    
    # GET /api/usuarios/roles/buscar/?nombre=<nombre> - Buscar rol por nombre
    path('roles/buscar/', RolBuscarView.as_view(), name='rol-buscar'),
    
    
    # ==================== RUTAS DE USUARIO ====================
    # POST /api/usuarios/login/ - Login de usuario (NO requiere autenticación)
    path('login/', UsuarioLoginView.as_view(), name='usuario-login'),
    
    # POST /api/usuarios/registrar/ - Registrar nuevo cliente (NO requiere autenticación)
    path('registrar/', UsuarioRegistrarView.as_view(), name='usuario-registrar'),
    
    # GET /api/usuarios/ - Listar todos los usuarios
    # POST /api/usuarios/ - Crear un nuevo usuario
    path('', UsuarioListCreateView.as_view(), name='usuario-list-create'),
    
    # GET /api/usuarios/<id>/ - Obtener un usuario
    # PUT /api/usuarios/<id>/ - Actualizar un usuario completamente
    # PATCH /api/usuarios/<id>/ - Actualizar un usuario parcialmente
    # DELETE /api/usuarios/<id>/ - Desactivar un usuario (soft delete)
    path('<int:id_usuario>/', UsuarioDetailView.as_view(), name='usuario-detail'),
    
    # DELETE /api/usuarios/<id>/permanente/ - Eliminar permanentemente un usuario
    path('<int:id_usuario>/permanente/', UsuarioDeletePermanentView.as_view(), name='usuario-delete-permanent'),
    
    # POST /api/usuarios/cambiar-password/ - Cambiar contraseña
    path('cambiar-password/', UsuarioCambiarPasswordView.as_view(), name='usuario-cambiar-password'),
    
    # GET /api/usuarios/buscar/?q=<query> - Buscar usuarios
    path('buscar/', UsuarioBuscarView.as_view(), name='usuario-buscar'),
    
    # PATCH /api/usuarios/<id>/fcm-token/ - Actualizar FCM token
    path('<int:id_usuario>/fcm-token/', UsuarioActualizarFCMTokenView.as_view(), name='usuario-fcm-token'),
]
