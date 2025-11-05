from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from .models import Usuario


class CustomJWTAuthentication(JWTAuthentication):
    """
    Autenticación JWT personalizada que usa el modelo Usuario
    en lugar del modelo de usuario por defecto de Django.
    """
    
    def get_user(self, validated_token):
        """
        Obtiene el usuario desde el token validado usando el modelo Usuario personalizado.
        """
        try:
            user_id = validated_token.get('user_id')
            if user_id is None:
                raise InvalidToken('Token no contiene user_id')
            
            # Usar el modelo Usuario personalizado
            user = Usuario.objects.get(idUsuario=user_id, activo=True)
            return user
            
        except Usuario.DoesNotExist:
            raise InvalidToken('Usuario no encontrado o inactivo')
