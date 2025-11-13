"""
Vistas API para el sistema de reportes dinámicos.
Maneja peticiones de texto y audio para generar reportes personalizados.
"""
import logging
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser
from django.http import JsonResponse

from .parser import parse_prompt
from .voice_processor import process_voice_prompt
from .query_builder import build_report_query
from .generators import generate_report
from usuarios.permissions import IsSuperAdmin

logger = logging.getLogger(__name__)


class DynamicReportView(APIView):
    """
    Vista API para generar reportes dinámicos desde prompts de texto.
    
    POST /api/reportes/dynamic_report/
    Body:
    {
        "prompt": "reporte de productos activos de este mes en excel",
        "format": "excel"  // opcional, se puede extraer del prompt
    }
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    parser_classes = []
    
    def post(self, request):
        try:
            prompt = request.body.decode("utf-8").strip()
           
            
            # Validar entrada
            if not prompt:
                return Response({
                    'error': 'Se requiere un prompt de texto',
                    'code': 'MISSING_PROMPT'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Usuario {request.user.username} solicitó reporte: {prompt}")
            
            # 1. Parsear prompt
            try:
                params = parse_prompt(prompt)
                
                
                
                if params.get('errors'):
                    return Response({
                        'error': 'Error analizando el prompt',
                        'details': params['errors'],
                        'code': 'PARSE_ERROR'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                logger.debug(f"Parámetros parseados: {params}")
                
            except Exception as e:
                logger.error(f"Error parseando prompt: {e}")
                return Response({
                    'error': 'Error interno analizando el prompt',
                    'code': 'PARSE_EXCEPTION'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 2. Construir consulta
            try:
                queryset, headers = build_report_query(params)
                
                if not queryset.exists():
                    return Response({
                        'message': 'La consulta no arrojó resultados',
                        'count': 0,
                        'data': []
                    }, status=status.HTTP_200_OK)
                
                logger.info(f"Consulta construida. Resultados: ~{queryset.count()}")
                
            except Exception as e:
                logger.error(f"Error construyendo consulta: {e}")
                return Response({
                    'error': 'Error construyendo la consulta de datos',
                    'details': str(e),
                    'code': 'QUERY_ERROR'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 3. Generar reporte
            try:
                report_format = params.get('format', 'excel')
                title = self._generate_title(params)
                
                if report_format == 'json':
                    # Devolver JSON para visualización en pantalla
                    # Normalizar los datos para evitar undefined
                    data = self._normalize_queryset_data(queryset, headers)
                    return Response({
                        'title': title,
                        'headers': headers,
                        'data': data,
                        'count': len(data),
                        'format': 'json'
                    }, status=status.HTTP_200_OK)
                else:
                    # Generar archivo descargable
                    return generate_report(queryset, headers, report_format, title)
                    
            except Exception as e:
                logger.error(f"Error generando reporte: {e}")
                return Response({
                    'error': 'Error generando el reporte',
                    'details': str(e),
                    'code': 'GENERATION_ERROR'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error inesperado en DynamicReportView: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'code': 'INTERNAL_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_title(self, params: dict) -> str:
        """Genera un título descriptivo para el reporte."""
        module = params.get('module', 'Datos').capitalize()
        title_parts = [f"Reporte de {module}"]
        
        # Agregar filtros al título
        filters = params.get('filters', {})
        if filters.get('categoria'):
            title_parts.append(f"Categoría: {filters['categoria']}")
        if filters.get('activo') is not None:
            estado = "Activos" if filters['activo'] else "Inactivos"
            title_parts.append(estado)
        
        # Agregar rango de fechas si existe
        date_range = params.get('date_range', {})
        if date_range.get('start_date'):
            fecha_str = date_range['start_date'].strftime('%b %Y')
            title_parts.append(f"({fecha_str})")
        
        return " - ".join(title_parts)
    
    def _normalize_queryset_data(self, queryset, headers: list) -> list:
        """
        Normaliza los datos del queryset para evitar valores undefined en frontend.
        Asegura que cada fila tenga exactamente los campos especificados en headers.
        """
        normalized_data = []
        
        for item in queryset:
            if isinstance(item, dict):
                # Para QuerySets con .values()
                normalized_item = {}
                
                # Crear mapeo basado en las claves disponibles en el item
                item_keys = list(item.keys())
                
                for i, header in enumerate(headers):
                    value = None
                    
                    # Intentar mapear el header con las claves disponibles
                    if i < len(item_keys):
                        key = item_keys[i]
                        value = item.get(key)
                    else:
                        # Buscar por nombre similar
                        value = self._find_value_by_header(item, header)
                    
                    # Formatear el valor
                    normalized_item[header] = self._format_value(value)
                        
                normalized_data.append(normalized_item)
            else:
                # Para objetos modelo
                normalized_item = {}
                for header in headers:
                    # Mapear headers a atributos del modelo
                    attr_name = self._header_to_attribute(header)
                    value = getattr(item, attr_name, None)
                    normalized_item[header] = self._format_value(value)
                        
                normalized_data.append(normalized_item)
        
        return normalized_data
    
    def _find_value_by_header(self, item_dict: dict, header: str):
        """Busca un valor en el diccionario basado en el header."""
        # Mapeo de headers a posibles claves en el QuerySet
        header_mappings = {
            'Categoría': ['categoria__nombre', 'categoria_nombre', 'product__categoria__nombre'],
            'Total Productos': ['total_productos', 'conteo_productos'],
            'Total Variantes': ['total_variantes'],
            'Stock Total': ['stock_total'],
            'Precio Promedio': ['precio_promedio', 'avg_price'],
            'Precio Mínimo': ['precio_min', 'min_price'], 
            'Precio Máximo': ['precio_max', 'max_price'],
            'ID': ['id', 'idCategoria', 'idUsuario'],
            'ID Producto': ['product__id'],
            'Producto': ['product__name'],
            'Nombre': ['name', 'nombre'],
            'Descripción': ['description', 'descripcion'],
            'Precio Base': ['base_price'],
            'Precio': ['price'],
            'Activo': ['active', 'activo', 'product__active'],
            'Fecha Creación': ['created_at', 'fecha_creacion', 'product__created_at'],
            'Username': ['username'],
            'Email': ['email'],
            'Teléfono': ['telefono'],
            'Rol': ['rol__nombre'],
            'Fecha Registro': ['fecha_creacion'],
            'Mes': ['mes'],
            'Productos Activos': ['productos_activos'],
            'Cantidad Usuarios': ['count'],
            'Stock': ['stock'],
            'SKU': ['sku'],
            'Talla': ['size'],
            'Color': ['color'],
            'Modelo': ['model_name']
        }
        
        possible_keys = header_mappings.get(header, [header.lower().replace(' ', '_')])
        
        for key in possible_keys:
            if key in item_dict:
                return item_dict[key]
        
        # Si no encuentra nada, usar el primer valor None como fallback
        return None
    
    def _format_value(self, value):
        """Formatea un valor para evitar undefined en frontend."""
        if value is None:
            return ""
        elif hasattr(value, 'strftime'):  # Es una fecha
            return value.strftime('%d/%m/%Y %H:%M')
        elif isinstance(value, bool):
            return "Sí" if value else "No"
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            return str(value)
    
    def _header_to_attribute(self, header: str) -> str:
        """Convierte un header legible a nombre de atributo del modelo."""
        mapping = {
            'ID': 'id',
            'Nombre': 'name',
            'Descripción': 'description',
            'Precio Base': 'base_price',
            'Categoría': 'categoria__nombre',
            'Activo': 'active',
            'Fecha Creación': 'created_at',
            'Email': 'email',
            'Username': 'username',
            'Teléfono': 'telefono',
            'Rol': 'rol__nombre',
            'Fecha Registro': 'fecha_creacion'
        }
        return mapping.get(header, header.lower().replace(' ', '_'))


class VoiceReportView(APIView):
    """
    Vista API para generar reportes dinámicos desde prompts de voz.
    
    POST /api/reportes/voice_report/
    Content-Type: multipart/form-data
    Body:
    - audio_file: Archivo de audio (WAV, MP3, etc.)
    - format: Formato de salida opcional
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    parser_classes = [MultiPartParser]
    
    def post(self, request):
        try:
            audio_file = request.FILES.get('audio_file')
            format_override = request.data.get('format', '').strip().lower()
            
            # Validar entrada
            if not audio_file:
                return Response({
                    'error': 'Se requiere un archivo de audio',
                    'code': 'MISSING_AUDIO'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Usuario {request.user.username} subió archivo de audio: {audio_file.name}")
            
            # 1. Procesar audio
            try:
                params = process_voice_prompt(audio_file)
                
                if params.get('errors'):
                    return Response({
                        'error': 'Error procesando el audio',
                        'details': params['errors'],
                        'code': 'AUDIO_PROCESSING_ERROR'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Aplicar formato override
                if format_override and format_override in ['excel', 'pdf', 'csv', 'json']:
                    params['format'] = format_override
                
                logger.debug(f"Audio procesado. Texto: {params.get('original_prompt', 'N/A')}")
                
            except Exception as e:
                logger.error(f"Error procesando audio: {e}")
                return Response({
                    'error': 'Error interno procesando el audio',
                    'code': 'AUDIO_EXCEPTION'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 2. Construir consulta (mismo proceso que texto)
            try:
                queryset, headers = build_report_query(params)
                
                if not queryset.exists():
                    return Response({
                        'message': 'La consulta no arrojó resultados',
                        'audio_text': params.get('original_prompt', ''),
                        'count': 0,
                        'data': []
                    }, status=status.HTTP_200_OK)
                
            except Exception as e:
                logger.error(f"Error construyendo consulta desde audio: {e}")
                return Response({
                    'error': 'Error construyendo la consulta de datos',
                    'audio_text': params.get('original_prompt', ''),
                    'details': str(e),
                    'code': 'QUERY_ERROR'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 3. Generar reporte
            try:
                report_format = params.get('format', 'excel')
                title = self._generate_title(params)
                
                if report_format == 'json':
                    # Respuesta JSON con datos normalizados
                    data = self._normalize_queryset_data(queryset, headers)
                    return Response({
                        'title': title,
                        'headers': headers,
                        'data': data,
                        'count': len(data),
                        'audio_text': params.get('original_prompt', ''),
                        'format': 'json'
                    }, status=status.HTTP_200_OK)
                else:
                    # Archivo descargable
                    return generate_report(queryset, headers, report_format, title)
                    
            except Exception as e:
                logger.error(f"Error generando reporte desde audio: {e}")
                return Response({
                    'error': 'Error generando el reporte',
                    'audio_text': params.get('original_prompt', ''),
                    'details': str(e),
                    'code': 'GENERATION_ERROR'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error inesperado en VoiceReportView: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'code': 'INTERNAL_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_title(self, params: dict) -> str:
        """Genera un título descriptivo para el reporte."""
        # Mismo método que DynamicReportView
        module = params.get('module', 'Datos').capitalize()
        title_parts = [f"Reporte de {module}"]
        
        filters = params.get('filters', {})
        if filters.get('categoria'):
            title_parts.append(f"Categoría: {filters['categoria']}")
        if filters.get('activo') is not None:
            estado = "Activos" if filters['activo'] else "Inactivos"
            title_parts.append(estado)
        
        date_range = params.get('date_range', {})
        if date_range.get('start_date'):
            fecha_str = date_range['start_date'].strftime('%b %Y')
            title_parts.append(f"({fecha_str})")
        
        return " - ".join(title_parts)


class ReportStatusView(APIView):
    """
    Vista para consultar el estado del sistema de reportes.
    
    GET /api/reportes/status/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Devuelve el estado de las capacidades del sistema."""
        # Verificar disponibilidad de librerías
        try:
            import openpyxl
            excel_available = True
        except ImportError:
            excel_available = False
        
        try:
            import reportlab
            pdf_available = True
        except ImportError:
            pdf_available = False
        
        try:
            import speech_recognition
            voice_available = True
        except ImportError:
            voice_available = False
        
        return Response({
            'system_status': 'operational',
            'capabilities': {
                'text_reports': True,
                'voice_reports': voice_available,
                'excel_export': excel_available,
                'pdf_export': pdf_available,
                'csv_export': True,
                'json_export': True
            },
            'supported_modules': ['productos', 'categorias', 'usuarios', 'ventas'],
            'user_permissions': {
                'can_generate_reports': hasattr(request.user, 'rol') and request.user.rol and request.user.rol.nombre == 'SuperAdmin',
                'is_super_admin': hasattr(request.user, 'rol') and request.user.rol and request.user.rol.nombre == 'SuperAdmin'
            }
        }, status=status.HTTP_200_OK)