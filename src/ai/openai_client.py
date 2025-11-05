"""
OpenAI API-Client
"""

import os
import time
from openai import OpenAI
from typing import Optional, Dict, List
from dotenv import load_dotenv
from src.utils.logger import get_logger

# Lade Environment-Variablen
load_dotenv()

logger = get_logger(__name__)


class OpenAIClient:
    """Client für OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialisiert den OpenAI Client
        
        Args:
            api_key: OpenAI API-Key (falls nicht aus Environment)
            model: Modell-Name (falls nicht aus Environment)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-5')
        
        if not self.api_key or self.api_key == 'your_openai_api_key_here':
            raise ValueError("OpenAI API-Key nicht gesetzt! Bitte konfigurieren Sie OPENAI_API_KEY in .env")
        
        # Entferne mögliche proxies-Umgebungsvariablen die Probleme verursachen können
        proxies_backup = {}
        for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY']:
            if key in os.environ:
                proxies_backup[key] = os.environ.pop(key)
        
        # Versuche verschiedene Methoden zur Client-Erstellung
        client_creation_errors = []
        
        # Versuch 1: Standard Client ohne zusätzliche Parameter
        try:
            self.client = OpenAI(api_key=self.api_key)
        except TypeError as e:
            if 'proxies' in str(e) or 'http_client' in str(e):
                # Spezifischer Fehler für Proxy-bezogene Probleme
                try:
                    # Versuche, einen httpx-Client ohne Proxy-Einstellungen zu erstellen
                    import httpx
                    http_client = httpx.Client(
                        timeout=60.0,
                        # Explizit keine Proxy-Einstellungen
                    )
                    self.client = OpenAI(
                        api_key=self.api_key,
                        http_client=http_client
                    )
                    logger.info("OpenAI Client erfolgreich mit eigenem HTTP-Client erstellt")
                except Exception as e2:
                    client_creation_errors.append(f"Proxy-spezifischer Versuch fehlgeschlagen: {e2}")
                    # Fallback zu Standard-Initialisierung
                    self.client = OpenAI(api_key=self.api_key)
                    logger.info("OpenAI Client mit Standard-Initialisierung erstellt")
            else:
                # Ein anderer TypeError - werfe ihn
                raise e
        except Exception as e:
            client_creation_errors.append(f"Genereller Fehler: {e}")
            # Versuche Standard-Client als Fallback
            self.client = OpenAI(api_key=self.api_key)
            logger.warning(f"OpenAI Client mit Fallback-Initialisierung erstellt nach Fehler: {e}")
        finally:
            # Stelle Umgebungsvariablen wieder her
            os.environ.update(proxies_backup)
    
    def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> str:
        """
        Generiert Text mit OpenAI API mit Retry-Logik
        
        Args:
            system_prompt: System-Prompt
            user_prompt: User-Prompt
            temperature: Temperature (0.0-2.0)
            max_tokens: Maximale Anzahl Tokens
            max_retries: Maximale Anzahl Wiederholungsversuche
            retry_delay: Basis-Verzögerung zwischen Wiederholungen (exponential backoff)
            
        Returns:
            Generierter Text
            
        Raises:
            Exception: Wenn alle Wiederholungsversuche fehlgeschlagen sind
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                # Versuche zuerst mit max_completion_tokens (neuere API)
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=temperature,
                        max_completion_tokens=max_tokens  # Neuer Parametername
                    )
                except TypeError:
                    # Fallback zu max_tokens (ältere API)
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                
                return response.choices[0].message.content.strip()
            
            except Exception as e:
                last_exception = e
                error_msg = str(e)
                
                # Prüfe ob es ein temporärer Fehler ist (Rate Limit, Server Error)
                is_retryable = (
                    "rate_limit" in error_msg.lower() or
                    "500" in error_msg or
                    "502" in error_msg or
                    "503" in error_msg or
                    "429" in error_msg or
                    "timeout" in error_msg.lower()
                )
                
                if attempt < max_retries and is_retryable:
                    # Exponential backoff
                    delay = retry_delay * (2 ** attempt)
                    logger.warning(
                        f"OpenAI API-Fehler (Versuch {attempt + 1}/{max_retries + 1}): {error_msg}. "
                        f"Wiederhole in {delay:.1f} Sekunden..."
                    )
                    time.sleep(delay)
                else:
                    # Nicht wiederholbar oder keine Versuche mehr
                    if not is_retryable:
                        logger.error(f"OpenAI API-Fehler (nicht wiederholbar): {error_msg}")
                        raise Exception(f"Fehler bei OpenAI API-Aufruf: {error_msg}")
                    else:
                        logger.error(f"OpenAI API-Fehler nach {max_retries + 1} Versuchen: {error_msg}")
        
        # Alle Versuche fehlgeschlagen
        raise Exception(f"Fehler bei OpenAI API-Aufruf nach {max_retries + 1} Versuchen: {str(last_exception)}")
    
    def generate_text_with_vision(
        self,
        system_prompt: str,
        user_prompt: str,
        image_path: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> str:
        """
        Generiert Text mit Vision-API (für Screenshot-Analyse) mit Retry-Logik
        
        Args:
            system_prompt: System-Prompt
            user_prompt: User-Prompt
            image_path: Pfad zum Bild
            temperature: Temperature
            max_tokens: Maximale Anzahl Tokens
            max_retries: Maximale Anzahl Wiederholungsversuche
            retry_delay: Basis-Verzögerung zwischen Wiederholungen (exponential backoff)
            
        Returns:
            Generierter Text
            
        Raises:
            Exception: Wenn alle Wiederholungsversuche fehlgeschlagen sind
        """
        import base64
        
        # Encode Bild als base64
        try:
            with open(image_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Fehler beim Lesen des Bildes: {e}", exc_info=True)
            raise Exception(f"Fehler beim Lesen des Bildes: {str(e)}")
        
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_data}"
                        }
                    }
                ]
            }
        ]
        
        # Verwende gpt-5 oder gpt-4o für Vision (GPT-5 unterstützt Vision)
        if "gpt-5" in self.model.lower():
            vision_model = "gpt-5"
        elif "gpt-4o" in self.model.lower():
            vision_model = "gpt-4o"
        else:
            vision_model = "gpt-4-vision-preview"
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                # Versuche zuerst mit max_completion_tokens (neuere API)
                try:
                    response = self.client.chat.completions.create(
                        model=vision_model,
                        messages=messages,
                        temperature=temperature,
                        max_completion_tokens=max_tokens  # Neuer Parametername
                    )
                except TypeError:
                    # Fallback zu max_tokens (ältere API)
                    response = self.client.chat.completions.create(
                        model=vision_model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                
                return response.choices[0].message.content.strip()
            
            except Exception as e:
                last_exception = e
                error_msg = str(e)
                
                # Prüfe ob es ein temporärer Fehler ist
                is_retryable = (
                    "rate_limit" in error_msg.lower() or
                    "500" in error_msg or
                    "502" in error_msg or
                    "503" in error_msg or
                    "429" in error_msg or
                    "timeout" in error_msg.lower()
                )
                
                if attempt < max_retries and is_retryable:
                    delay = retry_delay * (2 ** attempt)
                    logger.warning(
                        f"OpenAI Vision API-Fehler (Versuch {attempt + 1}/{max_retries + 1}): {error_msg}. "
                        f"Wiederhole in {delay:.1f} Sekunden..."
                    )
                    time.sleep(delay)
                else:
                    if not is_retryable:
                        logger.error(f"OpenAI Vision API-Fehler (nicht wiederholbar): {error_msg}")
                        raise Exception(f"Fehler bei OpenAI Vision API-Aufruf: {error_msg}")
                    else:
                        logger.error(f"OpenAI Vision API-Fehler nach {max_retries + 1} Versuchen: {error_msg}")
        
        raise Exception(f"Fehler bei OpenAI Vision API-Aufruf nach {max_retries + 1} Versuchen: {str(last_exception)}")
    
    def is_available(self) -> bool:
        """
        Prüft ob API verfügbar ist
        
        Returns:
            True wenn API verfügbar ist
        """
        try:
            # Teste API-Verbindung
            self.client.models.list()
            return True
        except Exception:
            return False


