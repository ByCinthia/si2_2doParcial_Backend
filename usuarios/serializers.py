from rest_framework import serializers
from .models import Rol, Usuario


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
            'idUsuario', 'username', 'email', 'password', 'fcmToken',
            'rol', 'fecha_creacion', 'fecha_actualizacion', 'activo'
        ]
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
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


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    idRol = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'fcmToken', 'idRol']
    
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
    
    def create(self, validated_data):
        # Mapear idRol a rol para crear el usuario
        id_rol = validated_data.pop('idRol')
        from .models import Rol
        rol = Rol.objects.get(idRol=id_rol)
        validated_data['rol'] = rol
        
        password = validated_data.pop('password')
        usuario = Usuario(**validated_data)
        usuario.set_password(password)
        usuario.save()
        return usuario


class UsuarioLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UsuarioDetailSerializer(serializers.ModelSerializer):
    rol = RolSerializer(read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'idUsuario', 'username', 'email', 'fcmToken',
            'rol', 'fecha_creacion', 'fecha_actualizacion', 'activo'
        ]
