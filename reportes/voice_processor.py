"""
Procesador de audio para convertir prompts de voz a texto.
Integra con servicios de speech-to-text para análisis de reportes por voz.
"""
import logging
import tempfile
import base64
from django.conf import settings
from django.core.files.base import ContentFile
from .parser import parse_prompt

logger = logging.getLogger(__name__)

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.warning("speech_recognition no está instalado. Funcionalidad de voz limitada.")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("openai no está instalado. API de OpenAI no disponible.")


class VoiceProcessor:
    """Procesador de archivos de audio para convertir a texto."""
    
    def __init__(self):
        self.recognizer = None
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            # Configuración optimizada para español
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            self.recognizer.phrase_threshold = 0.3
    
    def process_audio_file(self, audio_file) -> dict:
        """
        Procesa un archivo de audio y lo convierte a texto.
        
        Args:
            audio_file: Archivo de audio (puede ser UploadedFile o bytes)
            
        Returns:
            dict: Resultado con texto extraído y parámetros del reporte
        """
        if not SPEECH_RECOGNITION_AVAILABLE:
            return {
                'success': False,
                'error': 'Procesamiento de voz no disponible. Instale speech_recognition.',
                'text': '',
                'parsed_params': {}
            }
        
        try:
            # Guardar archivo temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                if hasattr(audio_file, 'read'):
                    temp_file.write(audio_file.read())
                else:
                    temp_file.write(audio_file)
                temp_file_path = temp_file.name
            
            # Convertir audio a texto
            text = self._audio_to_text(temp_file_path)
            
            if not text:
                return {
                    'success': False,
                    'error': 'No se pudo extraer texto del audio',
                    'text': '',
                    'parsed_params': {}
                }
            
            logger.info(f"Texto extraído del audio: {text}")
            
            # Analizar el texto extraído
            parsed_params = parse_prompt(text)
            
            return {
                'success': True,
                'error': None,
                'text': text,
                'parsed_params': parsed_params
            }
            
        except Exception as e:
            logger.error(f"Error procesando audio: {e}")
            return {
                'success': False,
                'error': f'Error procesando audio: {str(e)}',
                'text': '',
                'parsed_params': {}
            }
    
    def process_base64_audio(self, audio_base64: str, format_hint: str = 'wav') -> dict:
        """
        Procesa audio codificado en base64.
        
        Args:
            audio_base64: Audio en formato base64
            format_hint: Sugerencia del formato (wav, mp3, etc.)
            
        Returns:
            dict: Resultado del procesamiento
        """
        try:
            # Decodificar base64
            audio_data = base64.b64decode(audio_base64)
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{format_hint}') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Convertir a texto
            text = self._audio_to_text(temp_file_path)
            
            if not text:
                return {
                    'success': False,
                    'error': 'No se pudo extraer texto del audio',
                    'text': '',
                    'parsed_params': {}
                }
            
            # Analizar texto
            parsed_params = parse_prompt(text)
            
            return {
                'success': True,
                'error': None,
                'text': text,
                'parsed_params': parsed_params
            }
            
        except Exception as e:
            logger.error(f"Error procesando audio base64: {e}")
            return {
                'success': False,
                'error': f'Error procesando audio: {str(e)}',
                'text': '',
                'parsed_params': {}
            }
    
    def _audio_to_text(self, audio_file_path: str) -> str:
        """
        Convierte archivo de audio a texto usando diferentes métodos.
        """
        text = ''
        
        # Método 1: OpenAI Whisper (si está disponible)
        if OPENAI_AVAILABLE and hasattr(settings, 'OPENAI_API_KEY'):
            try:
                text = self._whisper_transcribe(audio_file_path)
                if text:
                    logger.info("Transcripción exitosa con OpenAI Whisper")
                    return text
            except Exception as e:
                logger.warning(f"Falló transcripción con Whisper: {e}")
        
        # Método 2: Google Speech Recognition (gratis)
        try:
            text = self._google_transcribe(audio_file_path)
            if text:
                logger.info("Transcripción exitosa con Google Speech Recognition")
                return text
        except Exception as e:
            logger.warning(f"Falló transcripción con Google: {e}")
        
        # Método 3: SpeechRecognition offline (limitado)
        try:
            text = self._offline_transcribe(audio_file_path)
            if text:
                logger.info("Transcripción exitosa offline")
                return text
        except Exception as e:
            logger.warning(f"Falló transcripción offline: {e}")
        
        return text
    
    def _whisper_transcribe(self, audio_path: str) -> str:
        """Transcribe usando OpenAI Whisper."""
        if not OPENAI_AVAILABLE:
            return ''
        
        try:
            client = openai.OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', ''))
            
            with open(audio_path, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="es"  # Forzar español
                )
            
            return transcript.text.strip()
        except Exception as e:
            logger.error(f"Error en Whisper: {e}")
            return ''
    
    def _google_transcribe(self, audio_path: str) -> str:
        """Transcribe usando Google Speech Recognition."""
        if not self.recognizer:
            return ''
        
        try:
            with sr.AudioFile(audio_path) as source:
                # Ajustar para ruido ambiente
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(source)
            
            # Reconocimiento en español
            text = self.recognizer.recognize_google(audio, language='es-ES')
            return text.strip()
            
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition no pudo entender el audio")
            return ''
        except sr.RequestError as e:
            logger.error(f"Error en el servicio de Google Speech Recognition: {e}")
            return ''
        except Exception as e:
            logger.error(f"Error inesperado en Google transcription: {e}")
            return ''
    
    def _offline_transcribe(self, audio_path: str) -> str:
        """Transcripción offline básica (muy limitada)."""
        # Esta función sería para implementar con bibliotecas offline como vosk
        # Por ahora retorna vacío
        logger.warning("Transcripción offline no implementada")
        return ''


def process_voice_prompt(audio_file) -> dict:
    """
    Función de conveniencia para procesar un prompt de voz.
    
    Args:
        audio_file: Archivo de audio a procesar
        
    Returns:
        dict: Parámetros extraídos del prompt de voz
    """
    processor = VoiceProcessor()
    result = processor.process_audio_file(audio_file)
    
    if result['success']:
        return result['parsed_params']
    else:
        return {
            'module': None,
            'format': 'excel',
            'date_range': {},
            'group_by': None,
            'filters': {},
            'errors': [result['error']],
            'original_prompt': result['text'] or 'Audio no procesado'
        }