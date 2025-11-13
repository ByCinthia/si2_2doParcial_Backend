"""
Serializers para validación de datos en el sistema de reportes.
"""
from rest_framework import serializers


class DynamicReportSerializer(serializers.Serializer):
    """Serializer para validar peticiones de reportes dinámicos."""
    
    prompt = serializers.CharField(
        max_length=1000,
        help_text="Prompt en español describiendo el reporte deseado"
    )
    format = serializers.ChoiceField(
        choices=['excel', 'pdf', 'csv', 'json'],
        required=False,
        default='excel',
        help_text="Formato de salida del reporte"
    )
    
    def validate_prompt(self, value):
        """Valida que el prompt no esté vacío y sea seguro."""
        if not value.strip():
            raise serializers.ValidationError("El prompt no puede estar vacío")
        
        # Validaciones de seguridad básicas
        dangerous_keywords = ['delete', 'drop', 'truncate', 'insert', 'update']
        prompt_lower = value.lower()
        
        for keyword in dangerous_keywords:
            if keyword in prompt_lower:
                raise serializers.ValidationError(
                    f"El prompt contiene palabras no permitidas: {keyword}"
                )
        
        return value.strip()


class VoiceReportSerializer(serializers.Serializer):
    """Serializer para validar peticiones de reportes por voz."""
    
    audio_file = serializers.FileField(
        help_text="Archivo de audio con el prompt hablado"
    )
    format = serializers.ChoiceField(
        choices=['excel', 'pdf', 'csv', 'json'],
        required=False,
        default='excel',
        help_text="Formato de salida del reporte"
    )
    
    def validate_audio_file(self, value):
        """Valida el archivo de audio."""
        # Validar tamaño (máximo 10MB)
        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError(
                "El archivo de audio no puede superar los 10MB"
            )
        
        # Validar tipo de archivo
        allowed_types = [
            'audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/ogg',
            'audio/webm', 'audio/flac', 'audio/x-wav'
        ]
        
        if value.content_type and value.content_type not in allowed_types:
            raise serializers.ValidationError(
                f"Tipo de archivo no permitido: {value.content_type}. "
                f"Permitidos: WAV, MP3, OGG, WebM, FLAC"
            )
        
        return value


class ReportParametersSerializer(serializers.Serializer):
    """Serializer para validar parámetros de reportes estructurados."""
    
    module = serializers.ChoiceField(
        choices=['productos', 'categorias', 'usuarios', 'ventas'],
        required=True,
        help_text="Módulo del cual generar el reporte"
    )
    format = serializers.ChoiceField(
        choices=['excel', 'pdf', 'csv', 'json'],
        default='excel',
        help_text="Formato de salida"
    )
    group_by = serializers.ChoiceField(
        choices=['categoria', 'usuario', 'producto', 'mes', 'estado'],
        required=False,
        help_text="Campo de agrupación"
    )
    start_date = serializers.DateTimeField(
        required=False,
        help_text="Fecha de inicio del rango"
    )
    end_date = serializers.DateTimeField(
        required=False,
        help_text="Fecha de fin del rango"
    )
    filters = serializers.DictField(
        required=False,
        help_text="Filtros adicionales como diccionario"
    )
    
    def validate(self, data):
        """Validaciones cruzadas."""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # Validar que end_date sea posterior a start_date
        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError(
                "La fecha de fin debe ser posterior a la fecha de inicio"
            )
        
        return data
    
    def validate_filters(self, value):
        """Valida los filtros aplicados."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Los filtros deben ser un diccionario")
        
        # Validar claves de filtros permitidas
        allowed_filter_keys = [
            'categoria', 'nombre', 'activo', 'precio_min', 'precio_max',
            'stock_min', 'stock_max', 'usuario', 'rol'
        ]
        
        for key in value.keys():
            if key not in allowed_filter_keys:
                raise serializers.ValidationError(
                    f"Filtro no permitido: {key}. "
                    f"Permitidos: {allowed_filter_keys}"
                )
        
        return value