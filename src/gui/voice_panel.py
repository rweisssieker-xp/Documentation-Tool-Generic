"""
Voice Control Panel - GUI for voice-first documentation.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
import threading

from src.utils.logger import get_logger

logger = get_logger(__name__)


class VoiceControlPanel(ttk.Frame):
    """
    Panel for voice recording and transcription control.
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        on_transcription: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        """
        Initialize voice control panel.
        
        Args:
            parent: Parent widget
            on_transcription: Callback for transcribed text
        """
        super().__init__(parent, **kwargs)
        
        self.on_transcription = on_transcription
        self._is_recording = False
        self._voice_capture = None
        self._whisper_client = None
        
        self._setup_ui()
        self._try_initialize_voice()
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Title
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(
            title_frame,
            text="🎤 Sprachsteuerung",
            font=("Segoe UI", 11, "bold")
        ).pack(side=tk.LEFT)
        
        self._status_label = ttk.Label(
            title_frame,
            text="⚫ Bereit",
            foreground="gray"
        )
        self._status_label.pack(side=tk.RIGHT)
        
        # Separator
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=5)
        
        # Recording controls
        control_frame = ttk.Frame(self)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self._record_btn = ttk.Button(
            control_frame,
            text="⏺️ Aufnahme starten",
            command=self._toggle_recording,
            width=20
        )
        self._record_btn.pack(side=tk.LEFT, padx=5)
        
        self._pause_btn = ttk.Button(
            control_frame,
            text="⏸️ Pause",
            command=self._toggle_pause,
            state=tk.DISABLED,
            width=10
        )
        self._pause_btn.pack(side=tk.LEFT, padx=5)
        
        # Transcription display
        trans_frame = ttk.LabelFrame(self, text="Transkription")
        trans_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self._transcription_text = tk.Text(
            trans_frame,
            height=4,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self._transcription_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Command help
        help_frame = ttk.LabelFrame(self, text="Sprachbefehle")
        help_frame.pack(fill=tk.X, padx=10, pady=5)
        
        help_text = """
• "Notiz: [Text]" - Fügt Notiz hinzu
• "Wichtig: [Text]" - Fügt Warnung hinzu
• "Pause" / "Weiter" - Pausiert/Fortsetzt
• "Stoppe Aufnahme" - Beendet Aufnahme
        """
        
        ttk.Label(
            help_frame,
            text=help_text,
            font=("Segoe UI", 9),
            foreground="gray"
        ).pack(padx=5, pady=5)
    
    def _try_initialize_voice(self):
        """Try to initialize voice components."""
        try:
            from src.voice import VoiceCapture, WhisperClient
            
            self._voice_capture = VoiceCapture()
            
            # Check for API key before initializing Whisper
            import os
            if os.getenv("OPENAI_API_KEY"):
                self._whisper_client = WhisperClient()
                self._update_status("✅ Bereit", "green")
            else:
                self._update_status("⚠️ API-Key fehlt", "orange")
        
        except ImportError as e:
            logger.warning(f"Voice modules not available: {e}")
            self._update_status("❌ Nicht verfügbar", "red")
            self._record_btn.configure(state=tk.DISABLED)
        except Exception as e:
            logger.error(f"Voice initialization failed: {e}")
            self._update_status(f"❌ Fehler", "red")
    
    def _toggle_recording(self):
        """Toggle recording state."""
        if not self._is_recording:
            self._start_recording()
        else:
            self._stop_recording()
    
    def _start_recording(self):
        """Start voice recording."""
        if not self._voice_capture:
            messagebox.showerror("Fehler", "Sprachaufnahme nicht verfügbar")
            return
        
        try:
            self._voice_capture.start_recording(
                session_id="gui_session",
                on_chunk=self._on_audio_chunk
            )
            
            self._is_recording = True
            self._record_btn.configure(text="⏹️ Aufnahme stoppen")
            self._pause_btn.configure(state=tk.NORMAL)
            self._update_status("🔴 Aufnahme läuft", "red")
        
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            messagebox.showerror("Fehler", f"Aufnahme konnte nicht gestartet werden:\n{e}")
    
    def _stop_recording(self):
        """Stop voice recording."""
        if self._voice_capture:
            audio_path = self._voice_capture.stop_recording()
            
            if audio_path and self._whisper_client:
                # Transcribe in background
                threading.Thread(
                    target=self._transcribe_audio,
                    args=(audio_path,),
                    daemon=True
                ).start()
        
        self._is_recording = False
        self._record_btn.configure(text="⏺️ Aufnahme starten")
        self._pause_btn.configure(state=tk.DISABLED)
        self._update_status("✅ Bereit", "green")
    
    def _toggle_pause(self):
        """Toggle pause state."""
        if not self._voice_capture:
            return
        
        if self._voice_capture._is_paused:
            self._voice_capture.resume_recording()
            self._pause_btn.configure(text="⏸️ Pause")
            self._update_status("🔴 Aufnahme läuft", "red")
        else:
            self._voice_capture.pause_recording()
            self._pause_btn.configure(text="▶️ Fortsetzen")
            self._update_status("⏸️ Pausiert", "orange")
    
    def _on_audio_chunk(self, audio_bytes: bytes, chunk_path: str):
        """Handle audio chunk for real-time transcription."""
        if self._whisper_client:
            threading.Thread(
                target=self._transcribe_chunk,
                args=(chunk_path,),
                daemon=True
            ).start()
    
    def _transcribe_chunk(self, audio_path: str):
        """Transcribe an audio chunk."""
        try:
            result = self._whisper_client.transcribe_file(audio_path)
            self.after(0, lambda: self._append_transcription(result.text))
        except Exception as e:
            logger.error(f"Chunk transcription failed: {e}")
    
    def _transcribe_audio(self, audio_path: str):
        """Transcribe complete audio file."""
        try:
            result = self._whisper_client.transcribe_file(audio_path)
            self.after(0, lambda: self._set_transcription(result.text))
            
            if self.on_transcription:
                self.after(0, lambda: self.on_transcription(result.text))
        
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            self.after(0, lambda: messagebox.showerror(
                "Fehler", f"Transkription fehlgeschlagen:\n{e}"
            ))
    
    def _append_transcription(self, text: str):
        """Append text to transcription display."""
        self._transcription_text.configure(state=tk.NORMAL)
        self._transcription_text.insert(tk.END, text + " ")
        self._transcription_text.configure(state=tk.DISABLED)
        self._transcription_text.see(tk.END)
    
    def _set_transcription(self, text: str):
        """Set transcription display."""
        self._transcription_text.configure(state=tk.NORMAL)
        self._transcription_text.delete(1.0, tk.END)
        self._transcription_text.insert(tk.END, text)
        self._transcription_text.configure(state=tk.DISABLED)
    
    def _update_status(self, text: str, color: str):
        """Update status label."""
        self._status_label.configure(text=text, foreground=color)
    
    def get_transcription(self) -> str:
        """Get current transcription text."""
        return self._transcription_text.get(1.0, tk.END).strip()

