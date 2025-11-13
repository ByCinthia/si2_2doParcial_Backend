from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Rutas de tus apps
    path('api/usuarios/', include('usuarios.urls')),
    path('api/productos/', include('productos.urls')),
    path('api/categorias/', include('categorias.urls')),
    path('api/ventas/', include('ventas.urls')),
    path('api/reportes/', include('reportes.urls')),

    # Rutas JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),  # 🔹 Añadido para verificación
]
