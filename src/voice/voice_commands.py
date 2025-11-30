"""
Voice Commands Module - Process voice commands for hands-free control.
Part of Feature 7: Voice-First Documentation
"""

import re
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum

from src.utils.logger import get_logger

logger = get_logger(__name__)


class CommandType(Enum):
    """Types of voice commands."""
    SESSION_CONTROL = "session_control"
    STEP_CONTROL = "step_control"
    ANNOTATION = "annotation"
    EXPORT = "export"
    NAVIGATION = "navigation"
    QUERY = "query"
    UNKNOWN = "unknown"


@dataclass
class VoiceCommand:
    """Parsed voice command."""
    type: CommandType
    action: str
    parameters: Dict[str, Any]
    original_text: str
    confidence: float


class VoiceCommandProcessor:
    """
    Processes transcribed text to extract voice commands.
    Supports multiple languages (German and English).
    """
    
    # Command patterns for German
    GERMAN_PATTERNS = {
        # Session control
        r'(starte?|beginne?)\s*(die\s*)?(session|aufnahme|dokumentation)': ('SESSION_CONTROL', 'start'),
        r'(stoppe?|beende?)\s*(die\s*)?(session|aufnahme|dokumentation)': ('SESSION_CONTROL', 'stop'),
        r'(pausiere?|pause)\s*(die\s*)?(session|aufnahme)?': ('SESSION_CONTROL', 'pause'),
        r'(weiter|fortsetzen|fortfahren)': ('SESSION_CONTROL', 'resume'),
        
        # Step control
        r'(rückgängig|zurück|undo)': ('STEP_CONTROL', 'undo'),
        r'(wiederholen|redo|nochmal)': ('STEP_CONTROL', 'redo'),
        r'(lösche?n?|entferne?n?)\s*(den\s*)?(letzten\s*)?(schritt)?': ('STEP_CONTROL', 'delete_last'),
        r'(neuer|nächster)\s*schritt': ('STEP_CONTROL', 'new_step'),
        
        # Annotations
        r'(notiz|anmerkung|hinweis)[:\s]*(.+)': ('ANNOTATION', 'add_note'),
        r'(wichtig|achtung|warnung)[:\s]*(.+)': ('ANNOTATION', 'add_warning'),
        r'(tipp|empfehlung)[:\s]*(.+)': ('ANNOTATION', 'add_tip'),
        
        # Export
        r'(exportiere?n?|speichere?n?)\s*(als\s*)?(pdf|word|docx|markdown|html)': ('EXPORT', 'export'),
        r'(generiere?|erstelle?)\s*(das\s*)?(dokument|dokumentation)': ('EXPORT', 'generate'),
        
        # Navigation
        r'(gehe?\s*zu|springe?\s*zu)\s*(schritt\s*)?(\d+)': ('NAVIGATION', 'goto_step'),
        r'(zum\s*)?(anfang|start)': ('NAVIGATION', 'goto_start'),
        r'(zum\s*)?(ende|schluss)': ('NAVIGATION', 'goto_end'),
    }
    
    # Command patterns for English
    ENGLISH_PATTERNS = {
        # Session control
        r'(start|begin)\s*(the\s*)?(session|recording|documentation)?': ('SESSION_CONTROL', 'start'),
        r'(stop|end)\s*(the\s*)?(session|recording|documentation)?': ('SESSION_CONTROL', 'stop'),
        r'(pause)\s*(the\s*)?(session|recording)?': ('SESSION_CONTROL', 'pause'),
        r'(resume|continue)': ('SESSION_CONTROL', 'resume'),
        
        # Step control
        r'(undo|go\s*back)': ('STEP_CONTROL', 'undo'),
        r'(redo|repeat)': ('STEP_CONTROL', 'redo'),
        r'(delete|remove)\s*(the\s*)?(last\s*)?(step)?': ('STEP_CONTROL', 'delete_last'),
        r'(new|next)\s*step': ('STEP_CONTROL', 'new_step'),
        
        # Annotations
        r'(note|annotation)[:\s]*(.+)': ('ANNOTATION', 'add_note'),
        r'(important|warning|caution)[:\s]*(.+)': ('ANNOTATION', 'add_warning'),
        r'(tip|recommendation)[:\s]*(.+)': ('ANNOTATION', 'add_tip'),
        
        # Export
        r'(export|save)\s*(as\s*)?(pdf|word|docx|markdown|html)': ('EXPORT', 'export'),
        r'(generate|create)\s*(the\s*)?(document|documentation)': ('EXPORT', 'generate'),
        
        # Navigation
        r'(go\s*to|jump\s*to)\s*(step\s*)?(\d+)': ('NAVIGATION', 'goto_step'),
        r'(to\s*the\s*)?(beginning|start)': ('NAVIGATION', 'goto_start'),
        r'(to\s*the\s*)?(end)': ('NAVIGATION', 'goto_end'),
    }
    
    def __init__(self, primary_language: str = 'de'):
        """
        Initialize voice command processor.
        
        Args:
            primary_language: Primary language ('de' or 'en')
        """
        self.primary_language = primary_language
        self._command_handlers: Dict[str, Callable] = {}
        
        # Compile patterns
        self._patterns = {}
        if primary_language == 'de':
            self._patterns.update(self._compile_patterns(self.GERMAN_PATTERNS))
            self._patterns.update(self._compile_patterns(self.ENGLISH_PATTERNS))  # Fallback
        else:
            self._patterns.update(self._compile_patterns(self.ENGLISH_PATTERNS))
            self._patterns.update(self._compile_patterns(self.GERMAN_PATTERNS))  # Fallback
        
        logger.info(f"VoiceCommandProcessor initialized: {primary_language}")
    
    def _compile_patterns(self, patterns: Dict[str, tuple]) -> Dict[re.Pattern, tuple]:
        """Compile regex patterns."""
        return {re.compile(pattern, re.IGNORECASE): action for pattern, action in patterns.items()}
    
    def register_handler(self, command_type: str, action: str, handler: Callable) -> None:
        """
        Register a handler for a specific command.
        
        Args:
            command_type: Type of command (e.g., 'SESSION_CONTROL')
            action: Action name (e.g., 'start')
            handler: Callback function to execute
        """
        key = f"{command_type}:{action}"
        self._command_handlers[key] = handler
        logger.debug(f"Registered handler: {key}")
    
    def parse_command(self, text: str) -> Optional[VoiceCommand]:
        """
        Parse text to extract a voice command.
        
        Args:
            text: Transcribed text to parse
            
        Returns:
            VoiceCommand if found, None otherwise
        """
        text = text.strip().lower()
        
        if not text:
            return None
        
        for pattern, (command_type, action) in self._patterns.items():
            match = pattern.search(text)
            if match:
                # Extract parameters from match groups
                parameters = {}
                groups = match.groups()
                
                if action == 'add_note' and len(groups) >= 2:
                    parameters['content'] = groups[-1].strip() if groups[-1] else ''
                elif action == 'add_warning' and len(groups) >= 2:
                    parameters['content'] = groups[-1].strip() if groups[-1] else ''
                elif action == 'add_tip' and len(groups) >= 2:
                    parameters['content'] = groups[-1].strip() if groups[-1] else ''
                elif action == 'export' and groups:
                    for g in groups:
                        if g and g.lower() in ['pdf', 'word', 'docx', 'markdown', 'html']:
                            parameters['format'] = g.lower()
                            break
                elif action == 'goto_step' and groups:
                    for g in groups:
                        if g and g.isdigit():
                            parameters['step_number'] = int(g)
                            break
                
                command = VoiceCommand(
                    type=CommandType[command_type],
                    action=action,
                    parameters=parameters,
                    original_text=text,
                    confidence=0.9 if len(text) < 50 else 0.7
                )
                
                logger.info(f"Parsed command: {command_type}:{action} from '{text}'")
                return command
        
        logger.debug(f"No command found in: '{text}'")
        return None
    
    def execute_command(self, command: VoiceCommand) -> bool:
        """
        Execute a parsed command.
        
        Args:
            command: VoiceCommand to execute
            
        Returns:
            True if command was executed successfully
        """
        key = f"{command.type.value}:{command.action}"
        handler = self._command_handlers.get(key)
        
        if handler:
            try:
                handler(command.parameters)
                logger.info(f"Executed command: {key}")
                return True
            except Exception as e:
                logger.error(f"Command execution failed: {e}")
                return False
        else:
            logger.warning(f"No handler for command: {key}")
            return False
    
    def process_text(self, text: str) -> Optional[VoiceCommand]:
        """
        Parse and execute a voice command from text.
        
        Args:
            text: Transcribed text
            
        Returns:
            VoiceCommand if found and executed, None otherwise
        """
        command = self.parse_command(text)
        if command:
            self.execute_command(command)
        return command
    
    def get_help_text(self, language: str = 'de') -> str:
        """
        Get help text with available commands.
        
        Args:
            language: Language for help text
            
        Returns:
            Help text string
        """
        if language == 'de':
            return """
Verfügbare Sprachbefehle:

🎤 SESSION-STEUERUNG:
  • "Starte Aufnahme" / "Beginne Session"
  • "Stoppe Aufnahme" / "Beende Session"
  • "Pause" / "Weiter"

✏️ SCHRITT-STEUERUNG:
  • "Rückgängig" / "Undo"
  • "Wiederholen" / "Redo"
  • "Lösche letzten Schritt"
  • "Neuer Schritt"

📝 ANMERKUNGEN:
  • "Notiz: [Text]"
  • "Wichtig: [Text]"
  • "Tipp: [Text]"

📤 EXPORT:
  • "Exportiere als PDF/Word/Markdown"
  • "Generiere Dokument"

🧭 NAVIGATION:
  • "Gehe zu Schritt [Nummer]"
  • "Zum Anfang" / "Zum Ende"
"""
        else:
            return """
Available Voice Commands:

🎤 SESSION CONTROL:
  • "Start recording" / "Begin session"
  • "Stop recording" / "End session"
  • "Pause" / "Resume"

✏️ STEP CONTROL:
  • "Undo" / "Go back"
  • "Redo" / "Repeat"
  • "Delete last step"
  • "New step"

📝 ANNOTATIONS:
  • "Note: [text]"
  • "Important: [text]"
  • "Tip: [text]"

📤 EXPORT:
  • "Export as PDF/Word/Markdown"
  • "Generate document"

🧭 NAVIGATION:
  • "Go to step [number]"
  • "To the beginning" / "To the end"
"""

