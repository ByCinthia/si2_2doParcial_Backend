"""
Configuración y validaciones de seguridad para el sistema de reportes.
"""
import logging
from django.conf import settings
from django.core.cache import cache
from datetime import datetime, timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)

# Configuración por defecto
DEFAULT_CONFIG = {
    # Límites de datos
    'MAX_ROWS_PER_REPORT': 10000,
    'MAX_REPORTS_PER_USER_PER_HOUR': 10,
    'MAX_AUDIO_FILE_SIZE_MB': 10,
    'MAX_PROMPT_LENGTH': 1000,
    
    # Timeouts
    'QUERY_TIMEOUT_SECONDS': 30,
    'VOICE_PROCESSING_TIMEOUT_SECONDS': 60,
    
    # Formatos permitidos
    'ALLOWED_AUDIO_FORMATS': [
        'audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/ogg',
        'audio/webm', 'audio/flac', 'audio/x-wav'
    ],
    'ALLOWED_EXPORT_FORMATS': ['excel', 'pdf', 'csv', 'json'],
    
    # Módulos habilitados
    'ENABLED_MODULES': ['productos', 'categorias', 'usuarios'],
    
    # Palabras prohibidas en prompts
    'FORBIDDEN_KEYWORDS': [
        'delete', 'drop', 'truncate', 'insert', 'update', 'alter',
        'create', 'grant', 'revoke', 'exec', 'execute', 'script'
    ]
}


def get_config(key: str, default=None):
    """Obtiene un valor de configuración."""
    # Intentar desde settings de Django primero
    reports_config = getattr(settings, 'REPORTS_CONFIG', {})
    
    if key in reports_config:
        return reports_config[key]
    
    # Fallback a configuración por defecto
    return DEFAULT_CONFIG.get(key, default)


class SecurityValidator:
    """Validador de seguridad para el sistema de reportes."""
    
    def __init__(self):
        self.forbidden_keywords = get_config('FORBIDDEN_KEYWORDS')
        self.max_rows = get_config('MAX_ROWS_PER_REPORT')
        self.max_prompt_length = get_config('MAX_PROMPT_LENGTH')
    
    def validate_prompt(self, prompt: str) -> tuple:
        """
        Valida un prompt de texto por seguridad.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if not prompt:
            return False, "Prompt vacío no permitido"
        
        # Validar longitud
        if len(prompt) > self.max_prompt_length:
            return False, f"Prompt demasiado largo (máximo {self.max_prompt_length} caracteres)"
        
        # Validar palabras prohibidas
        prompt_lower = prompt.lower()
        for keyword in self.forbidden_keywords:
            if keyword in prompt_lower:
                logger.warning(f"Prompt bloqueado por palabra prohibida: {keyword}")
                return False, f"Prompt contiene palabra prohibida: {keyword}"
        
        return True, None
    
    def validate_user_rate_limit(self, user) -> tuple:
        """
        Valida límites de velocidad por usuario.
        
        Returns:
            tuple: (is_within_limit, remaining_requests)
        """
        max_requests = get_config('MAX_REPORTS_PER_USER_PER_HOUR')
        cache_key = f"report_requests_user_{user.id}"
        
        # Obtener contador actual
        current_count = cache.get(cache_key, 0)
        
        if current_count >= max_requests:
            return False, 0
        
        # Incrementar contador
        cache.set(cache_key, current_count + 1, timeout=3600)  # 1 hora
        
        return True, max_requests - (current_count + 1)
    
    def validate_queryset_size(self, queryset) -> tuple:
        """
        Valida el tamaño del queryset por rendimiento.
        
        Returns:
            tuple: (is_valid, count, limited_queryset)
        """
        try:
            total_count = queryset.count()
            
            if total_count > self.max_rows:
                logger.warning(f"Queryset limitado de {total_count} a {self.max_rows} filas")
                limited_queryset = queryset[:self.max_rows]
                return False, total_count, limited_queryset
            
            return True, total_count, queryset
            
        except Exception as e:
            logger.error(f"Error validando tamaño de queryset: {e}")
            return False, 0, queryset.none()
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitiza un nombre de archivo."""
        # Remover caracteres peligrosos
        dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
        sanitized = filename
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Limitar longitud
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        return sanitized


class AuditLogger:
    """Logger de auditoría para reportes generados."""
    
    @staticmethod
    def log_report_request(user, prompt: str, module: str, success: bool, error_msg: str = None):
        """Registra una petición de reporte."""
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'user_id': user.id if user else None,
            'username': user.username if user else None,
            'prompt': prompt[:200],  # Limitar longitud por privacidad
            'module': module,
            'success': success,
            'error': error_msg
        }
        
        if success:
            logger.info(f"Reporte generado exitosamente: {log_data}")
        else:
            logger.warning(f"Fallo en generación de reporte: {log_data}")
    
    @staticmethod
    def log_voice_request(user, audio_filename: str, transcription: str, success: bool):
        """Registra una petición de reporte por voz."""
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'user_id': user.id if user else None,
            'username': user.username if user else None,
            'audio_file': audio_filename,
            'transcription': transcription[:200] if transcription else None,
            'success': success
        }
        
        logger.info(f"Petición de reporte por voz: {log_data}")


def validate_report_params(params: dict) -> tuple:
    """
    Valida parámetros de reporte de manera integral.
    
    Returns:
        tuple: (is_valid, sanitized_params, errors)
    """
    validator = SecurityValidator()
    errors = []
    sanitized_params = params.copy()
    
    # Validar módulo
    enabled_modules = get_config('ENABLED_MODULES')
    if params.get('module') not in enabled_modules:
        errors.append(f"Módulo no habilitado: {params.get('module')}")
    
    # Validar formato
    allowed_formats = get_config('ALLOWED_EXPORT_FORMATS')
    if params.get('format') not in allowed_formats:
        errors.append(f"Formato no permitido: {params.get('format')}")
    
    # Sanitizar filtros
    if 'filters' in sanitized_params:
        sanitized_filters = {}
        for key, value in sanitized_params['filters'].items():
            # Solo mantener filtros seguros
            if isinstance(value, (str, int, float, bool)):
                sanitized_filters[key] = value
        sanitized_params['filters'] = sanitized_filters
    
    is_valid = len(errors) == 0
    return is_valid, sanitized_params, errors


# Middleware de seguridad (opcional)
class ReportSecurityMiddleware:
    """Middleware para aplicar seguridad a nivel de petición."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.validator = SecurityValidator()
    
    def __call__(self, request):
        # Aplicar validaciones antes de procesar
        if request.path.startswith('/api/reportes/'):
            # Validar rate limiting si el usuario está autenticado
            if request.user.is_authenticated:
                is_within_limit, remaining = self.validator.validate_user_rate_limit(request.user)
                if not is_within_limit:
                    from django.http import JsonResponse
                    return JsonResponse({
                        'error': 'Límite de reportes por hora excedido',
                        'code': 'RATE_LIMIT_EXCEEDED'
                    }, status=429)
        
        response = self.get_response(request)
        return response