import logging
from rest_framework import serializers
from .models import Rol, Usuario
import re

logger = logging.getLogger(__name__)

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['idRol', 'nombre', 'descripcion']
        read_only_fields = ['idRol']


class UsuarioSerializer(serializers.ModelSerializer):
    rol = RolSerializer(read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'idUsuario', 'username', 'email', 'password', 'fcmToken', 'telefono',
            'rol', 'fecha_creacion', 'fecha_actualizacion', 'activo'
        ]
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        # Normalizar telefono si viene
        telefono = validated_data.get('telefono')
        if telefono:
            validated_data['telefono'] = self._format_telefono(telefono)
        
        # Manejar actualización de rol si viene en validated_data
        if 'rol_id' in validated_data:
            from .models import Rol
            rol_id = validated_data.pop('rol_id')
            if Rol.objects.filter(idRol=rol_id).exists():
                instance.rol_id = rol_id
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance

    def _format_telefono(self, value):
        # quitar todo lo que no sea dígito
        digits = re.sub(r'\D', '', str(value))
        # Si vienen 8 dígitos -> agregar prefijo 591
        if len(digits) == 8 and digits.isdigit():
            return '+591' + digits
        # Si vienen 11 dígitos y comienzan con 591 -> agregar +
        if len(digits) == 11 and digits.startswith('591'):
            return '+' + digits
        raise serializers.ValidationError("El teléfono debe ser 8 dígitos de Bolivia (ej: 7xxxxxxx) o incluir prefijo 591.")


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    idRol = serializers.IntegerField(write_only=True)
    telefono = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'fcmToken', 'idRol', 'telefono']
    
    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value
    
    def validate_username(self, value):
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está registrado.")
        return value
    
    def validate_idRol(self, value):
        from .models import Rol
        if not Rol.objects.filter(idRol=value).exists():
            raise serializers.ValidationError("El rol especificado no existe.")
        return value

    def validate_telefono(self, value):
        if not value:
            return value
        digits = re.sub(r'\D', '', str(value))
        if len(digits) == 8 and digits.isdigit():
            return '+591' + digits
        if len(digits) == 11 and digits.startswith('591'):
            return '+' + digits
        raise serializers.ValidationError("El teléfono debe ser 8 dígitos de Bolivia (ej: 7xxxxxxx) o incluir prefijo 591.")
    
    def create(self, validated_data):
        # Mapear idRol a rol para crear el usuario
        id_rol = validated_data.pop('idRol')
        telefono = validated_data.pop('telefono', None)
        from .models import Rol
        rol = Rol.objects.get(idRol=id_rol)
        validated_data['rol'] = rol
        
        password = validated_data.pop('password')
        # Si validate_telefono devolvió un formato, ya está normalizado (+591...)
        if telefono:
            validated_data['telefono'] = telefono
        
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario


class UsuarioLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = (data.get('username') or "").strip()
        email = (data.get('email') or "").strip()
        password = data.get('password') or ""

        # log inicial de intento (no incluir password en logs)
        logger.debug("Login attempt received: username=%s email=%s", username or "(none)", email or "(none)")

        # Validar que se proporcione username o email
        if not username and not email:
            logger.warning("Login validation failed: no username/email provided")
            raise serializers.ValidationError("Proporciona 'username' o 'email' junto con 'password'.")

        # Buscar usuario por username o email
        user = None
        try:
            if username:
                user = Usuario.objects.filter(username=username, activo=True).first()
                logger.debug("Lookup by username -> %s", "found" if user else "not found")
            if not user and email:
                user = Usuario.objects.filter(email=email, activo=True).first()
                logger.debug("Lookup by email -> %s", "found" if user else "not found")
        except Exception as e:
            logger.exception("Error buscando usuario en DB: %s", e)
            raise serializers.ValidationError("Error interno al autenticar")

        if not user:
            logger.info("Login failed: user not found for username/email: %s / %s", username, email)
            raise serializers.ValidationError("Credenciales inválidas")

        # Verificar la contraseña usando el método del modelo
        try:
            pw_ok = user.check_password(password)
        except Exception as e:
            logger.exception("Error verificando contraseña: %s", e)
            pw_ok = False

        logger.debug("Password check for user %s -> %s", user.username, "ok" if pw_ok else "fail")
        if not pw_ok:
            logger.info("Login failed: bad password for user %s", user.username)
            raise serializers.ValidationError("Credenciales inválidas")

        # Guardar el usuario validado en validated_data
        data['user'] = user
        return data


class UsuarioDetailSerializer(serializers.ModelSerializer):
    rol = RolSerializer(read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'idUsuario', 'username', 'email', 'fcmToken', 'telefono',
            'rol', 'fecha_creacion', 'fecha_actualizacion', 'activo'
        ]
