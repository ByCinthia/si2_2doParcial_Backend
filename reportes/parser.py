"""
Parser de prompts en español para generación de reportes dinámicos.
Analiza texto natural y extrae parámetros de filtrado, agrupación y formato.
"""
import re
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse as date_parse

logger = logging.getLogger(__name__)

# Patrones regex para extraer información del prompt
REPORT_TYPE_REGEX = re.compile(r'\b(productos?|articulos?|inventario|categorias?|usuarios?|clientes?|ventas?|pedidos?)\b', re.IGNORECASE)
FORMAT_REGEX = re.compile(r'\b(excel|pdf|csv|json)\b', re.IGNORECASE)
DATE_RANGE_REGEX = re.compile(r'(hoy|ayer|esta semana|este mes|este año|último mes|últimos? (\d+) (días?|semanas?|meses?))', re.IGNORECASE)
SPECIFIC_DATE_REGEX = re.compile(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', re.IGNORECASE)
GROUP_BY_REGEX = re.compile(r'\b(?:agrupado?|agrupar|grupo|por)\s+(?:por\s+)?(categoria|categorías|cliente|clientes|producto|productos|mes|fecha|estado)\b', re.IGNORECASE)
FILTER_REGEX = re.compile(r'\b(?:de|con|donde|que)\s+(.*?)\s+(?:igual|es|contiene?|mayor|menor|>=|<=|>|<|=)', re.IGNORECASE)

# Filtros específicos
CATEGORY_REGEX = re.compile(r'\b(?:categoria|categoría)\s+["\']?([^"\']+)["\']?', re.IGNORECASE)
PRICE_MAYOR_REGEX = re.compile(r'\b(?:precio|costo|valor)\s*(?:mayor\s+(?:que|a)|>|>=)\s*(\d+(?:\.\d+)?)', re.IGNORECASE)
PRICE_MENOR_REGEX = re.compile(r'\b(?:precio|costo|valor)\s*(?:menor\s+(?:que|a)|<|<=)\s*(\d+(?:\.\d+)?)', re.IGNORECASE)
PRICE_IGUAL_REGEX = re.compile(r'\b(?:precio|costo|valor)\s*(?:igual\s+a|igual|=)\s*(\d+(?:\.\d+)?)', re.IGNORECASE)

# Regex para filtros de stock
STOCK_MAYOR_REGEX = re.compile(r'\b(?:stock|inventario|cantidad)\s*(?:mayor\s+(?:que|a)|>|>=)\s*(\d+)', re.IGNORECASE)
STOCK_MENOR_REGEX = re.compile(r'\b(?:stock|inventario|cantidad)\s*(?:menor\s+(?:que|a)|<|<=)\s*(\d+)', re.IGNORECASE)
STOCK_IGUAL_REGEX = re.compile(r'\b(?:stock|inventario|cantidad)\s*(?:igual\s+a|igual|=|de)\s*(\d+)', re.IGNORECASE)

ACTIVE_REGEX = re.compile(r'\b(activos?|inactivos?|habilitados?|deshabilitados?)\b', re.IGNORECASE)


def parse_prompt(prompt_text: str) -> dict:
    """
    Analiza un prompt en español y extrae parámetros para generar reportes.
    
    Args:
        prompt_text (str): Texto del prompt a analizar
        
    Returns:
        dict: Diccionario con parámetros extraídos:
            - module: Módulo del reporte (productos, usuarios, ventas, etc.)
            - format: Formato de salida (excel, pdf, csv, json)
            - date_range: Rango de fechas (start_date, end_date)
            - group_by: Campo de agrupación
            - filters: Diccionario de filtros aplicados
            - errors: Lista de errores encontrados
    """
    result = {
        'module': None,
        'format': 'excel',  # Por defecto
        'date_range': {},
        'group_by': None,
        'filters': {},
        'errors': [],
        'original_prompt': prompt_text
    }
    
    logger.info(f"Analizando prompt: {prompt_text}")
    
    try:
        # 1. Extraer tipo de reporte/módulo
        module_match = REPORT_TYPE_REGEX.search(prompt_text)
        if module_match:
            module = module_match.group(1).lower()
            # Normalizar nombres de módulos
            if module in ['productos', 'producto', 'articulos', 'artículo', 'inventario']:
                result['module'] = 'productos'
            elif module in ['categorias', 'categoria', 'categorías', 'categoría']:
                result['module'] = 'categorias'
            elif module in ['usuarios', 'usuario', 'clientes', 'cliente']:
                result['module'] = 'usuarios'
            elif module in ['ventas', 'venta', 'pedidos', 'pedido']:
                result['module'] = 'ventas'
            logger.debug(f"Módulo detectado: {result['module']}")
        
        # 2. Extraer formato de salida
        format_match = FORMAT_REGEX.search(prompt_text)
        if format_match:
            result['format'] = format_match.group(1).lower()
            logger.debug(f"Formato detectado: {result['format']}")
        
        # 3. Extraer rango de fechas
        date_range = _extract_date_range(prompt_text)
        if date_range:
            result['date_range'] = date_range
            logger.debug(f"Rango de fechas: {date_range}")
        
        # 4. Extraer agrupación
        group_match = GROUP_BY_REGEX.search(prompt_text)
        if group_match:
            group = group_match.group(1).lower()
            # Normalizar agrupación
            if group in ['categoria', 'categorías', 'categoría']:
                result['group_by'] = 'categoria'
            elif group in ['cliente', 'clientes']:
                result['group_by'] = 'usuario'
            elif group in ['producto', 'productos']:
                result['group_by'] = 'producto'
            elif group in ['mes', 'fecha']:
                result['group_by'] = 'mes'
            else:
                result['group_by'] = group
            logger.debug(f"Agrupación detectada: {result['group_by']}")
        
        # 5. Extraer filtros específicos
        _extract_filters(prompt_text, result)
        
        # 6. Validaciones
        if not result['module']:
            result['errors'].append('No se pudo identificar el tipo de reporte')
        
        if result['errors']:
            logger.warning(f"Errores en el prompt: {result['errors']}")
        else:
            logger.info(f"Prompt analizado exitosamente: {result}")
            
    except Exception as e:
        logger.error(f"Error analizando prompt: {e}")
        result['errors'].append(f"Error procesando el prompt: {str(e)}")
    
    return result


def _extract_date_range(text: str) -> dict:
    """Extrae rangos de fechas del texto."""
    now = timezone.now()
    
    # Rangos relativos
    if re.search(r'\bhoy\b', text, re.IGNORECASE):
        return {
            'start_date': now.replace(hour=0, minute=0, second=0, microsecond=0),
            'end_date': now.replace(hour=23, minute=59, second=59, microsecond=999999)
        }
    
    if re.search(r'\bayer\b', text, re.IGNORECASE):
        yesterday = now - timedelta(days=1)
        return {
            'start_date': yesterday.replace(hour=0, minute=0, second=0, microsecond=0),
            'end_date': yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
        }
    
    if re.search(r'\besta semana\b', text, re.IGNORECASE):
        start_week = now - timedelta(days=now.weekday())
        return {
            'start_date': start_week.replace(hour=0, minute=0, second=0, microsecond=0),
            'end_date': now
        }
    
    if re.search(r'\beste mes\b', text, re.IGNORECASE):
        start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return {
            'start_date': start_month,
            'end_date': now
        }
    
    if re.search(r'\beste año\b', text, re.IGNORECASE):
        start_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        return {
            'start_date': start_year,
            'end_date': now
        }
    
    if re.search(r'\búltimo mes\b', text, re.IGNORECASE):
        end_last_month = now.replace(day=1) - timedelta(days=1)
        start_last_month = end_last_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return {
            'start_date': start_last_month,
            'end_date': end_last_month.replace(hour=23, minute=59, second=59, microsecond=999999)
        }
    
    # Rangos específicos como "últimos 30 días"
    range_match = re.search(r'últimos?\s+(\d+)\s+(días?|semanas?|meses?)', text, re.IGNORECASE)
    if range_match:
        number = int(range_match.group(1))
        unit = range_match.group(2).lower()
        
        if 'día' in unit:
            start_date = now - timedelta(days=number)
        elif 'semana' in unit:
            start_date = now - timedelta(weeks=number)
        elif 'mes' in unit:
            start_date = now - relativedelta(months=number)
        else:
            return {}
        
        return {
            'start_date': start_date.replace(hour=0, minute=0, second=0, microsecond=0),
            'end_date': now
        }
    
    # Fechas específicas
    date_matches = SPECIFIC_DATE_REGEX.findall(text)
    if date_matches:
        try:
            # Si hay dos fechas, usar como rango
            if len(date_matches) >= 2:
                start_date = date_parse(date_matches[0])
                end_date = date_parse(date_matches[1])
                return {
                    'start_date': timezone.make_aware(start_date) if timezone.is_naive(start_date) else start_date,
                    'end_date': timezone.make_aware(end_date) if timezone.is_naive(end_date) else end_date
                }
            # Si hay una fecha, usar ese día completo
            elif len(date_matches) == 1:
                single_date = date_parse(date_matches[0])
                if timezone.is_naive(single_date):
                    single_date = timezone.make_aware(single_date)
                return {
                    'start_date': single_date.replace(hour=0, minute=0, second=0, microsecond=0),
                    'end_date': single_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                }
        except Exception as e:
            logger.warning(f"Error parsing date: {e}")
    
    return {}


def _extract_filters(text: str, result: dict):
    """Extrae filtros específicos del texto."""
    filters = result['filters']
    
    # Filtro por categoría
    category_match = CATEGORY_REGEX.search(text)
    if category_match:
        filters['categoria'] = category_match.group(1).strip()
        logger.debug(f"Filtro categoría: {filters['categoria']}")
    
    # Filtro por precio - usando regex separados para mayor claridad
    price_mayor_match = PRICE_MAYOR_REGEX.search(text)
    if price_mayor_match:
        valor = float(price_mayor_match.group(1))
        filters['precio_min'] = valor
        logger.debug(f"Filtro precio mayor que: {valor}")
    
    price_menor_match = PRICE_MENOR_REGEX.search(text)
    if price_menor_match:
        valor = float(price_menor_match.group(1))
        filters['precio_max'] = valor
        logger.debug(f"Filtro precio menor que: {valor}")
    
    price_igual_match = PRICE_IGUAL_REGEX.search(text)
    if price_igual_match:
        valor = float(price_igual_match.group(1))
        filters['precio_exacto'] = valor
        logger.debug(f"Filtro precio igual a: {valor}")
    
    # Filtros de stock
    stock_mayor_match = STOCK_MAYOR_REGEX.search(text)
    if stock_mayor_match:
        valor = int(stock_mayor_match.group(1))
        filters['stock_min'] = valor
        logger.debug(f"Filtro stock mayor que: {valor}")
    
    stock_menor_match = STOCK_MENOR_REGEX.search(text)
    if stock_menor_match:
        valor = int(stock_menor_match.group(1))
        filters['stock_max'] = valor
        logger.debug(f"Filtro stock menor que: {valor}")
    
    stock_igual_match = STOCK_IGUAL_REGEX.search(text)
    if stock_igual_match:
        valor = int(stock_igual_match.group(1))
        filters['stock_exacto'] = valor
        logger.debug(f"Filtro stock igual a: {valor}")
        logger.debug(f"Filtro stock menor que: {valor}")
    
    # Filtro por estado activo
    active_match = ACTIVE_REGEX.search(text)
    if active_match:
        active_text = active_match.group(1).lower()
        if 'activo' in active_text or 'habilitado' in active_text:
            filters['activo'] = True
        elif 'inactivo' in active_text or 'deshabilitado' in active_text:
            filters['activo'] = False
        logger.debug(f"Filtro activo: {filters.get('activo')}")
    
    # Filtros de texto libre (nombres, descripciones)
    if 'con nombre' in text.lower():
        name_pattern = re.search(r'con nombre\s+["\']?([^"\']+)["\']?', text, re.IGNORECASE)
        if name_pattern:
            filters['nombre'] = name_pattern.group(1).strip()
            logger.debug(f"Filtro nombre: {filters['nombre']}")