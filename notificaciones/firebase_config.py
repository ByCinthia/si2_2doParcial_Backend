"""
Configuración de Firebase Admin SDK para notificaciones push.

IMPORTANTE: Necesitas obtener tu archivo de credenciales de Firebase:
1. Ve a Firebase Console: https://console.firebase.google.com/
2. Selecciona tu proyecto
3. Ve a Configuración del proyecto (ícono de engranaje)
4. Ve a la pestaña "Cuentas de servicio"
5. Click en "Generar nueva clave privada"
6. Guarda el archivo JSON descargado como 'firebase-credentials.json' en la raíz del proyecto
7. NO SUBAS este archivo a git (agrégalo a .gitignore)
"""

import firebase_admin
from firebase_admin import credentials, messaging
import os
from pathlib import Path

# Ruta al archivo de credenciales de Firebase
BASE_DIR = Path(__file__).resolve().parent.parent
FIREBASE_CREDENTIALS_PATH = BASE_DIR / 'firebase-credentials.json'

# Variable para saber si Firebase está inicializado
_firebase_initialized = False


def initialize_firebase():
    """
    Inicializa Firebase Admin SDK con las credenciales.
    Solo se debe llamar una vez al inicio de la aplicación.
    """
    global _firebase_initialized
    
    if _firebase_initialized:
        return True
    
    if not firebase_admin._apps:
        try:
            if os.path.exists(FIREBASE_CREDENTIALS_PATH):
                cred = credentials.Certificate(str(FIREBASE_CREDENTIALS_PATH))
                firebase_admin.initialize_app(cred)
                _firebase_initialized = True
                print("✅ Firebase inicializado correctamente")
                return True
            else:
                print("⚠️ Archivo de credenciales de Firebase no encontrado")
                print(f"   Busca el archivo en: {FIREBASE_CREDENTIALS_PATH}")
                return False
        except Exception as e:
            print(f"❌ Error al inicializar Firebase: {str(e)}")
            return False
    
    _firebase_initialized = True
    return True


def send_push_notification(fcm_token, title, body, data=None):
    """
    Envía una notificación push a un dispositivo específico.
    
    Args:
        fcm_token (str): Token FCM del dispositivo
        title (str): Título de la notificación
        body (str): Cuerpo/mensaje de la notificación
        data (dict, optional): Datos adicionales para la notificación
    
    Returns:
        tuple: (success: bool, message_id or error: str)
    """
    if not _firebase_initialized:
        return False, "Firebase no está inicializado"
    
    try:
        # Construir el mensaje
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=fcm_token,
        )
        
        # Enviar el mensaje
        response = messaging.send(message)
        return True, response
    except Exception as e:
        return False, str(e)


def send_push_notification_multicast(fcm_tokens, title, body, data=None):
    """
    Envía una notificación push a múltiples dispositivos.
    
    Args:
        fcm_tokens (list): Lista de tokens FCM de los dispositivos
        title (str): Título de la notificación
        body (str): Cuerpo/mensaje de la notificación
        data (dict, optional): Datos adicionales para la notificación
    
    Returns:
        tuple: (success_count: int, failure_count: int, responses: list)
    """
    if not _firebase_initialized:
        return 0, len(fcm_tokens), "Firebase no está inicializado"
    
    try:
        # Construir el mensaje multicast
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            tokens=fcm_tokens,
        )
        
        # Enviar el mensaje
        response = messaging.send_multicast(message)
        return response.success_count, response.failure_count, response.responses
    except Exception as e:
        return 0, len(fcm_tokens), str(e)


def send_notification_to_topic(topic, title, body, data=None):
    """
    Envía una notificación a un topic (tema) de Firebase.
    Útil para enviar a grupos de usuarios suscritos a un tema.
    
    Args:
        topic (str): Nombre del topic
        title (str): Título de la notificación
        body (str): Cuerpo/mensaje de la notificación
        data (dict, optional): Datos adicionales para la notificación
    
    Returns:
        tuple: (success: bool, message_id or error: str)
    """
    if not _firebase_initialized:
        return False, "Firebase no está inicializado"
    
    try:
        # Construir el mensaje
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            topic=topic,
        )
        
        # Enviar el mensaje
        response = messaging.send(message)
        return True, response
    except Exception as e:
        return False, str(e)
