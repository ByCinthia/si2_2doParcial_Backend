"""
Guía de uso del sistema de reportes dinámicos
=============================================

El sistema de reportes permite generar reportes personalizados usando prompts en español.

ENDPOINTS DISPONIBLES:
=====================

1. POST /api/reportes/dynamic_report/
   - Genera reportes desde prompts de texto
   - Content-Type: application/json
   - Requiere autenticación y rol SuperAdmin

2. POST /api/reportes/voice_report/
   - Genera reportes desde archivos de audio
   - Content-Type: multipart/form-data
   - Requiere autenticación y rol SuperAdmin

3. GET /api/reportes/status/
   - Consulta el estado del sistema de reportes
   - Requiere autenticación

EJEMPLOS DE USO:
===============

1. Reporte de texto (JSON):
curl -X POST http://localhost:8000/api/reportes/dynamic_report/ \
  -H "Authorization: Bearer TU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "reporte de productos agrupados por categoría", "format": "json"}'

2. Reporte de productos activos:
curl -X POST http://localhost:8000/api/reportes/dynamic_report/ \
  -H "Authorization: Bearer TU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "lista de productos activos de este mes en excel"}'

3. Reporte de usuarios por rol:
curl -X POST http://localhost:8000/api/reportes/dynamic_report/ \
  -H "Authorization: Bearer TU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "usuarios agrupados por rol en pdf"}'

4. Consultar estado del sistema:
curl -X GET http://localhost:8000/api/reportes/status/ \
  -H "Authorization: Bearer TU_ACCESS_TOKEN"

5. Reporte por voz:
curl -X POST http://localhost:8000/api/reportes/voice_report/ \
  -H "Authorization: Bearer TU_ACCESS_TOKEN" \
  -F "audio_file=@mi_audio.wav" \
  -F "format=json"

PROMPTS SOPORTADOS:
==================

Módulos:
- productos, artículos, inventario
- categorías, tipos
- usuarios, clientes
- ventas (limitado)

Formatos:
- excel (por defecto)
- pdf
- csv  
- json

Filtros:
- "productos activos"
- "categorías con más de 10 productos"
- "usuarios registrados esta semana"
- "productos de la categoría ropa"
- "artículos con precio mayor a 50"

Agrupación:
- "agrupados por categoría"
- "agrupados por rol"
- "por mes"

Fechas:
- "de este mes"
- "esta semana"
- "último mes"
- "últimos 30 días"

EJEMPLOS ESPECÍFICOS:
====================

✅ "reporte de productos activos agrupados por categoría en excel"
✅ "lista de usuarios registrados este mes en pdf"
✅ "categorías con sus productos en csv"
✅ "productos de la categoría ropa con stock menor a 10"
✅ "usuarios inactivos del último trimestre"

RESPUESTA JSON (format=json):
============================
{
    "title": "Reporte de Productos - Activos",
    "headers": ["ID", "Nombre", "Precio Base", "Categoría", "Stock"],
    "data": [
        {
            "ID": "1",
            "Nombre": "Producto 1",
            "Precio Base": "29.99",
            "Categoría": "Electrónicos",
            "Stock": "15"
        }
    ],
    "count": 1,
    "format": "json"
}

ARCHIVOS DESCARGABLES:
=====================
Para formatos excel, pdf, csv el endpoint devuelve directamente el archivo
con headers Content-Disposition para descarga automática.

CÓDIGOS DE ERROR:
================
- 400: MISSING_PROMPT - Falta el prompt
- 400: PARSE_ERROR - Error analizando el prompt  
- 403: Permisos insuficientes (no es SuperAdmin)
- 500: Errores internos del servidor

DEPENDENCIAS OPCIONALES:
=======================
- openpyxl: Para reportes Excel
- reportlab: Para reportes PDF
- speech_recognition: Para procesamiento de voz
- openai: Para transcripción con Whisper (opcional)

Sin estas librerías, las funcionalidades correspondientes estarán deshabilitadas
pero el sistema seguirá funcionando con las demás opciones.
"""

# Ejemplo de uso en Python
import requests

def ejemplo_reporte():
    # Configuración
    BASE_URL = "http://localhost:8000"
    TOKEN = "tu_access_token_aqui"
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Ejemplo 1: Reporte básico
    payload = {
        "prompt": "reporte de productos agrupados por categoría",
        "format": "json"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/reportes/dynamic_report/",
        json=payload,
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Título: {data['title']}")
        print(f"Headers: {data['headers']}")
        print(f"Registros: {data['count']}")
        print(f"Datos: {data['data'][:3]}")  # Primeros 3 registros
    else:
        print(f"Error: {response.status_code} - {response.text}")

# Ejemplo para obtener estado del sistema
def verificar_estado():
    BASE_URL = "http://localhost:8000"
    TOKEN = "tu_access_token_aqui"
    
    response = requests.get(
        f"{BASE_URL}/api/reportes/status/",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    
    if response.status_code == 200:
        status = response.json()
        print("Estado del sistema:")
        print(f"- Reportes de texto: {status['capabilities']['text_reports']}")
        print(f"- Reportes de voz: {status['capabilities']['voice_reports']}")  
        print(f"- Excel: {status['capabilities']['excel_export']}")
        print(f"- PDF: {status['capabilities']['pdf_export']}")
        print(f"- CSV: {status['capabilities']['csv_export']}")

if __name__ == "__main__":
    # Descomentar para probar
    # ejemplo_reporte()
    # verificar_estado()
    pass